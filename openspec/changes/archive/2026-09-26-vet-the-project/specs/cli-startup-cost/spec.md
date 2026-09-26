## ADDED Requirements

### Requirement: The vet command and the manifest reader load no geometry stack

The system SHALL keep manifest discovery and model declaration in a
module that imports nothing from the framework except the top-level
`machinome` package, and no third-party package. Importing that module
SHALL NOT import `machinome.core`, `machinome.node`, `numpy`, `trimesh`,
`cadquery` or `OCP`. `machinome.core.loader` SHALL import these names from
that module and re-export them, so that every existing importer of
`ProjectManifestError`, `MODEL_NAME`, `project_root` and `_find_manifest`
from the loader keeps receiving the same objects. `read_project`,
`select_model` and the `Model` and `Project` records stay in the loader,
which builds them from the manifest module's declaration and adds each
model's build directory; what they return is unchanged.

Dispatching `machinome vet` SHALL import the vet command's module, vet's
own modules and the manifest module. It SHALL import no other command's
module, no `machinome.core` or `machinome.node` module, and no CAD or
numeric backend.

#### Scenario: The manifest module is light

- **WHEN** the manifest module is imported in a fresh interpreter
- **THEN** no `machinome.core` or `machinome.node` module, and none of
  `numpy`, `trimesh`, `cadquery` or `OCP`, appears among the imported
  modules

#### Scenario: The loader re-exports the same objects

- **WHEN** a caller imports `ProjectManifestError` and `project_root` from
  `machinome.core.loader`
- **THEN** each is the same object the manifest module defines, and an
  error raised by the manifest module is caught by `except
  loader.ProjectManifestError`

#### Scenario: Dispatching vet loads only vet

- **WHEN** `machinome vet` runs to completion in a fresh interpreter
- **THEN** the process has imported the `vet` command's module and no
  other command's module, and `machinome.core.loader`, `numpy` and
  `cadquery` are absent from its imported modules
