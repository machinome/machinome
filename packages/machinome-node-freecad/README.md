# machinome-freecad

Native FreeCAD assembly integration for machinome.

Status: development authorized; implementation and empirical validation are
in progress. This package is not released or published.

The first use case is to simulate an authored robotic arm without redeclaring
its native joints, connector frames, or enabled limits. The adapter is a
separate optional dependency; machinome remains independently licensed under
Apache-2.0 and usable without FreeCAD.

The ratified interface imports `FreeCADAssemblyNode` and `FreeCADJoint` from
`machinome_freecad`. FreeCAD-specific loading, conversion, and runtime linkage
belong to this repository. See [the workflow record](workflow/ongoing/dume-native-freecad.md)
for evidence, scope, ratification, and the empirical validation discipline.

## Development

The native assembly cycle is developed in `WTs/native-freecad-assembly` using
repository-owned OpenSpec records: planning commit, red-first implementation,
adversarial review, then independent project validation before closeout.
The real project is an independent repository, not a fixture copied here.
FreeCAD and its bundled libraries are user-installed; this repository does
not redistribute a FreeCAD binary.

## License

Copyright (C) 2026 Luis Henrique Cassis Fagundes.

This library is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2.1 of the License, or (at your option)
any later version (SPDX: `LGPL-2.1-or-later`). See [LICENSE](LICENSE).

Third-party code retains its original copyrights and applicable licences.
Any incorporated or adapted source must carry its attribution and change
notice; permission to link does not replace those obligations.
