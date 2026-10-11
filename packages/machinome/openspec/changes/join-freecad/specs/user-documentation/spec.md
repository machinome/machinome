## ADDED Requirements

### Requirement: A native FreeCAD assembly is documented as a how-to

The manual SHALL carry a how-to guide, `howto/freecad-assemblies`, listed in
the how-to section of the navigation, that tells a reader how to simulate a
native FreeCAD assembly: the install line `pip install "machinome[freecad]"`;
the FreeCAD runtime the package was measured with, FreeCAD 1.1.4 for Linux
x86-64, extracted from its official AppImage and named by
`MACHINOME_FREECAD_ROOT`, which no extra installs; that only trusted documents
may be opened, since FreeCAD runs the Python a document carries; the
declaration, with `FreeCADAssemblyNode`, `freecad_source` and `FreeCADJoint`
imported from `machinome.node.freecad`; how a source path resolves; selection
by native internal Name; what the adapter reads (native zero, enabled limits)
and what it refuses (the supported graph, the constraint tolerances, saved-pose
drift); and that a changed source needs a fresh model and a fresh `Sim`.

The installation page SHALL list `machinome[freecad]` with the distribution it
installs and say that FreeCAD itself is found through
`MACHINOME_FREECAD_ROOT`; the how-to guide on choosing a part backend SHALL list
`FreeCADAssemblyNode` with `machinome.node.freecad` and `machinome[freecad]`;
the API reference SHALL document `FreeCADAssemblyNode` and `FreeCADJoint`
under `machinome.node.freecad`. No page a reader is sent to SHALL spell the
module `machinome_freecad`, and none SHALL link the package's archived working
record.

#### Scenario: A reader with a FreeCAD assembly looks for the task

- **WHEN** a reader opens the how-to section of the navigation
- **THEN** it lists the FreeCAD guide, whose example imports
  `FreeCADAssemblyNode` and `FreeCADJoint` from `machinome.node.freecad` and
  which names `MACHINOME_FREECAD_ROOT` and FreeCAD 1.1.4

#### Scenario: A reader picks the FreeCAD extra

- **WHEN** a reader looks up what to install for `FreeCADAssemblyNode`
- **THEN** the installation page names `machinome[freecad]` and
  `machinome-node-freecad` and says that FreeCAD is found through
  `MACHINOME_FREECAD_ROOT`, and the backends guide lists the class with its
  module and that extra

#### Scenario: No page spells the former module

- **WHEN** every page of the manual and the framework's README are read
- **THEN** none spells `machinome_freecad`
