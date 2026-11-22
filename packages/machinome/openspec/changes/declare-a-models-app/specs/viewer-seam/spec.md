## MODIFIED Requirements

### Requirement: The core declares the contract of viewers in one seam

The framework SHALL declare the contract of viewers in one module of its own,
`machinome.viewer` (`machinome/viewer/__init__.py`), importing nothing but the
standard library and `machinome.extras`. It SHALL state the contract version
it speaks as the integer `CONTRACT`, the operations a viewer may offer
(`present`, `capture`, `serve`, `embed`, `bundle`), and, as Protocols, what each
operation asks: every viewer its name, its `CONTRACT`, the operations it
offers, its identity, the node-tree document versions it reads (none, for a
viewer that reads no document) and whether a version is readable; `present`
and `withdraw`, preparing what the viewer reads at one assembled instant and
removing it; `capture`, an image of what was presented, with the snapshot
options the viewer honours; `serve`, an interactive session on a build
directory that can be told a build was published and can be stopped; `embed`,
the files an export or a documentation page carries and the report of the
installed viewer; `bundle`, a model's app bundled from its entry file and the
project's root into a directory, answering the names of the files written and
the project files read, or refusing with its sentence and writing nothing.
The seam SHALL name the viewers the core knows and the extra
that installs each, and the default viewer of each operation, and no other
module of the core SHALL name a viewer's technology.

The seam's `__path__` SHALL be extended with the namespace portions found on
`sys.path` that ship no `__init__.py` of their own
(`machinome._namespace_portions`), so a provider installed by another
distribution resolves in an editable workspace as it does from the wheels.

#### Scenario: Both providers resolve in the workspace

- **WHEN** `machinome.viewer.web` and `machinome.viewer.openscad` are
  imported in the repository's editable workspace
- **THEN** each resolves to the `__init__.py` of its own distribution's
  directory, and `machinome.viewer`'s path holds the core's directory followed
  by the providers'

#### Scenario: Both providers resolve from the wheels

- **WHEN** the core's, the viewer's and the OpenSCAD viewer's wheels are
  installed into one environment
- **THEN** both providers resolve from it

#### Scenario: The seam loads no viewer

- **WHEN** `machinome.viewer` is imported
- **THEN** no provider, web framework, browser driver or CAD library is
  imported

#### Scenario: Bundling an app has a default viewer

- **WHEN** a build asks which viewer bundles a model's app, with no flag and
  no viewer declared by the project
- **THEN** the seam answers `web`, and the contract version is unchanged

### Requirement: Each viewer declares what it offers

The web viewer, `machinome.viewer.web` of the distribution `machinome-viewer`,
SHALL offer `present`, `capture`, `serve`, `embed` and `bundle`, read the
document versions its widget declares, and honour, beyond the common snapshot
options (output, image size, time, camera), `--autocenter` and `--viewall`,
which describe what it does by default. The OpenSCAD viewer,
`machinome.viewer.openscad` of the distribution `machinome-viewer-openscad`,
SHALL offer `present` and `capture`, read no node-tree document, and honour
every snapshot option. Each provider SHALL import its machinery only when an
operation is called, so resolving it and asking its identity or the versions
it reads imports no web framework, browser driver or CAD library.

#### Scenario: The declarations

- **WHEN** both providers are resolved
- **THEN** the web viewer's `OPERATIONS` are `present`, `capture`, `serve`,
  `embed` and `bundle`, the OpenSCAD viewer's are `present` and `capture`,
  and each `CONTRACT` equals the seam's

#### Scenario: Asking whether a version is readable is cheap

- **WHEN** the builder asks the web viewer whether it reads document version
  13
- **THEN** the answer is given without importing the viewer's server, its
  capture, a web framework or a browser driver

#### Scenario: The OpenSCAD viewer does not bundle

- **WHEN** a build asks the `openscad` viewer to bundle a model's app
- **THEN** it is refused naming the build, bundling, the `openscad` viewer
  and `web` as the viewer that bundles
