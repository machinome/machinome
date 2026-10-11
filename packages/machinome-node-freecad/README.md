# machinome-freecad

Native FreeCAD assembly integration for machinome.

Status: experimental implementation accepted after independent originating-project
validation and primary adversarial review. Native constraint residual admission
rejects the untouched Dum-E assembly's inconsistent Fixed connection.
Independent native moving-pose and 180°/120° command comparisons passed against
the project-owned native correction; upstream remains untouched. See
[the review](workflow/archive/native-freecad-assembly/native-freecad-adversarial-review.md).
This package is not released, published or integrated into its primary branch.

The first use case is to simulate an authored robotic arm without redeclaring
its native joints, connector frames, or enabled limits. The adapter is a
separate optional dependency; machinome remains independently licensed under
Apache-2.0 and usable without FreeCAD.

The ratified interface imports `FreeCADAssemblyNode` and `FreeCADJoint` from
`machinome_freecad`. FreeCAD-specific loading, conversion, and runtime linkage
belong to this repository. See [the workflow record](workflow/archive/native-freecad-assembly/dume-native-freecad.md)
for evidence, scope, ratification, and the empirical validation discipline.

## Development

The native assembly cycle is developed in `WTs/native-freecad-assembly` using
repository-owned OpenSpec records: planning commit, red-first implementation,
adversarial review, then independent project validation before closeout.
The real project is an independent repository, not a fixture copied here.
FreeCAD and its bundled libraries are user-installed; this repository does
not redistribute a FreeCAD binary.

## Use a native assembly

The public contract and complete example are in [the API guide](docs/api.md).
Declare the native file and joint Names, then bind ordinary machinome drivers.
The project declares no replacement joint types, axes, frames, zeroes or limits.

The tested dependency is the locally prepared machinome 0.7.1 at
`8a8a26711bcd7fd33c6daf7f8866d10004574f8c`; its 0.7.1 distribution is not yet
on the public index. This adapter uses internal coordinate, exact-leaf and
source-currency seams and pins that exact version. See
[runtime and development setup](docs/runtime.md) before installing from this
source tree. Do not install a different version solely because an editable
checkout happens to expose newer source.

The measured native runtime is FreeCAD 1.1.4 on Linux x86-64, using its
official extracted AppImage and bundled Python. Set `MACHINOME_FREECAD_ROOT`
to that extraction's root, containing `AppRun` and `usr/`.

Open trusted FCStd documents only. Native document restoration executes Python
proxies. The worker separates processes and OCCT ABIs; it is not a security
sandbox. The adapter currently supports one native Assembly with one grounded,
connected tree of rigid fixed and revolute connections. Other workbenches,
loops, dynamics and inverse kinematics are outside this version.

Machinome 0.7.1's `vet` contract does not recognize this experimental package
or `freecad_source` yet. Building and simulation have been tested; a successful
adapter build is not a claim of `vet` conformance.

## Evidence and provenance

[Validation evidence](workflow/archive/native-freecad-assembly/implementation-evidence.md) records the
red/green commands and compatibility observations. [NOTICE.md](NOTICE.md)
records native API/source provenance. Adapter fixtures are original synthetic
CAD; Dum-E's upstream CAD remains in the separate project and is not included
in this package. All nine Dum-E occurrences match native FreeCAD across eight
poses; changing only the native maximum from 180° to 120° changes the unchanged
simulation from completing at 150° to stopping at 120°. This acceptance applies
to the explicitly corrected project copy, not to the inconsistent original.

## License

Copyright (C) 2026 Luis Henrique Cassis Fagundes.

This library is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2.1 of the License, or (at your option)
any later version (SPDX: `LGPL-2.1-or-later`). See [LICENSE](LICENSE).

Third-party code retains its original copyrights and applicable licences.
Any incorporated or adapted source must carry its attribution and change
notice; permission to link does not replace those obligations.
