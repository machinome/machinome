## RENAMED Requirements

- FROM: `### Requirement: Optional LGPL package and documented public contract`
- TO: `### Requirement: The FreeCAD node package and its documented public contract`

## MODIFIED Requirements

### Requirement: Native assembly declaration and selected coordinate reference

The system SHALL export `FreeCADAssemblyNode` and `FreeCADJoint` from `machinome.node.freecad`. A subclass SHALL declare `freecad_source` naming its FCStd source, resolved relative to the Python module declaring that attribute. A class-body `alias = FreeCADJoint("Joint001")` SHALL select the existing imported revolute coordinate by native internal Name and SHALL be accepted as the target of an ordinary `Driver.drives(alias)` relation. The reference SHALL accept no replacement axis, frame, zero, type or range. Native existence and coordinate compatibility SHALL be checked after native resolution and before relation binding and simulation graph compilation.

Importing the public module or declaring the Python class SHALL NOT open CAD or require a FreeCAD runtime. Realizing a native assembly SHALL resolve its source before instance relations or simulation enumeration consume it. Every model instance SHALL own fresh nodes, joint arguments and bound slots; native mechanics SHALL NOT be mutable class-shared state.

Positive Dum-E scenarios in this capability SHALL use the explicitly project-repaired, constraint-consistent native copy described below. The untouched pinned upstream source SHALL remain negative admission evidence; repaired-source success SHALL NOT be reported as acceptance of that untouched source.

#### Scenario: The ratified running example constructs and moves

- **WHEN** the following class is instantiated from a valid supported source and its simulation is run

```python
from machinome.node.freecad import FreeCADAssemblyNode, FreeCADJoint
from machinome.motion.ports import Time
from machinome.simulation import Driver, Sim

class DumE(FreeCADAssemblyNode):
    freecad_source = "cad/MA_Dum_E_v2_Assembly.FCStd"
    time = Time.running()
    turntable = FreeCADJoint("Joint001")
    turn = Driver(default=0, unit="deg")
    turn.drives(turntable)

sim = Sim(DumE(), dt=0.02)
command = sim.move("turn", to=150, duration=1.0)
sim.run(1.0)
```

- **THEN** the relation addresses the native `Joint001` coordinate without any project-authored joint, frame or mechanical-limit declaration

#### Scenario: Source resolution does not depend on process cwd

- **WHEN** a supported subclass declares a relative source and is instantiated from another working directory or through an inheriting subclass in another module
- **THEN** the source resolves from the module that declared `freecad_source`

#### Scenario: Native selectors are not display labels

- **WHEN** a reference names an editable Label instead of the native internal Name, or selects a missing or fixed joint
- **THEN** realization refuses it naming the source, selector and type where present, and reports the available moving native Names

#### Scenario: Two instances are independent

- **WHEN** two instances of one native assembly class are simulated at different turntable commands
- **THEN** each retains its own coordinate values and placements and neither changes shared class declarations or the other's pose

### Requirement: The FreeCAD node package and its documented public contract

The implementation SHALL be the distribution `machinome-node-freecad` of the machinome repository, in its directory `packages/machinome-node-freecad/`, importing as the package `machinome.node.freecad`, installed by the framework's extra `machinome[freecad]`, numbered with the framework and distributed under the licence of the whole set. It SHALL depend on the framework and SHALL require no FreeCAD-specific edits, monkeypatches or copied native implementation in the framework's core, which reaches it only through the table of supported node types. Any unavoidable core integration failure SHALL be reported as evidence before a separate framework change is proposed. Incorporated third-party material SHALL retain its original copyright/licence and change notices, recorded in the framework's `CREDITS.md`. The package SHALL NOT redistribute the provisioned FreeCAD binary, and no extra SHALL install FreeCAD.

The package SHALL document its public imports, source-path resolution, native selector Names, supported graph, optional runtime setup, supported machinome compatibility, command/status observation and source-refresh behavior in the framework's manual. The independent empirical author SHALL be able to construct and validate the simulation through that documented public API without calling adapter-private importer methods. Required native runtime absence SHALL fail clearly at point of use while plain imports and existing machinome-only models remain usable.

The package's tests SHALL run in the framework's suite where `MACHINOME_FREECAD_ROOT` is set, and each of its test modules SHALL be reported skipped, with a reason naming that variable, where it is not.

#### Scenario: Core remains independent

- **WHEN** machinome is installed and used without machinome-node-freecad or a FreeCAD runtime
- **THEN** its existing imports, supported builds and simulation behavior remain valid

#### Scenario: The documented example requires no private importer calls

- **WHEN** the independent Dum-E author follows the package public documentation
- **THEN** source realization, native coordinate selection and running commands work using FreeCADAssemblyNode, FreeCADJoint and the existing framework public APIs only

#### Scenario: Packaged provenance is retained

- **WHEN** wheel and source distributions are built and inspected
- **THEN** the package's licence texts are included, the worker is present, FreeCAD binaries and FCStd documents are absent, `machinome~=<version>` and `machinome-engine-brep~=<version>` are declared with the framework's version, and the framework's `CREDITS.md` records what the package calls and what its worker adapted

#### Scenario: The suite without a runtime skips the native tests

- **WHEN** the framework's suite runs where `MACHINOME_FREECAD_ROOT` is not set
- **THEN** each of the four FreeCAD test modules is reported skipped with a reason naming `MACHINOME_FREECAD_ROOT`, and none of their tests fails or errors
