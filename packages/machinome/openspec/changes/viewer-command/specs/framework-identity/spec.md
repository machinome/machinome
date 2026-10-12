## MODIFIED Requirements

### Requirement: The framework is the package directory `packages/machinome` of a monorepo

The repository `machinome/machinome` SHALL be a monorepo whose
distributions each live in a directory under `packages/` named as the
distribution: the framework, the distribution `machinome`, SHALL live at
`packages/machinome/`, with its import package, tests, manual,
architecture synthesis, decision records, OpenSpec records and working
record, and any other directory under `packages/` SHALL be a sibling
distribution of the same repository. Paths named in the framework's specs,
decision records and manual SHALL be read relative to `packages/machinome/`
unless they name the repository root.

The framework's extension packages, today the engines `machinome-engine-brep`
and `machinome-engine-mesh` and the node packages `machinome-node-cadquery`,
`machinome-node-build123d`, `machinome-node-step`, `machinome-node-molejo`,
`machinome-node-openscad`, `machinome-node-solid2`, `machinome-node-jscad`,
`machinome-node-stl` and `machinome-node-freecad`, and the OpenSCAD viewer
`machinome-viewer-openscad`, a provider of the framework's seam of viewers,
SHALL each be such a sibling, holding only its
manifest `pyproject.toml`, a `README.md` that names its install line and the
licence, the relative symbolic links `LICENSE` and `LICENSES` to the root's,
and its namespace portion at its address under `machinome/`, with no
`__init__.py` at the levels the framework's import package defines; a portion
that is a package directory, `machinome/node/openscad/`,
`machinome/node/freecad/` or `machinome/viewer/openscad/`, holds its own
`__init__.py` at its address, below
those levels, and its manifest's package search names that package. Its specs,
tests, decision records and manual pages SHALL be the framework's, those of a
package that joined the repository from a repository of its own
(`machinome-node-freecad`) included.

A product that joined the repository from a repository of its own and is not
an extension package, today the mechanics helpers `machinome-mechanics` and
the browser viewer `machinome-viewer` and the skills package
`machinome-skills`, SHALL keep its record in its
directory: `packages/machinome-mechanics/` SHALL hold its manifest
`pyproject.toml`, a `README.md` that names its install line and the licence,
its `CHANGELOG.md`, its `MANIFEST.in` and `.gitignore`, the relative symbolic
links `LICENSE` and `LICENSES` to the root's, its package directory
`machinome/mechanics/` with its own `__init__.py` and none at `machinome/`, its
`tests/`, its `openspec/` (its specs and archived changes) and its
`workflow/`; `packages/machinome-viewer/` SHALL hold the same entries, its
package directory `machinome/viewer/web/` with its own `__init__.py`, none at
`machinome/` nor at `machinome/viewer/`, and the widget inside it, its
`scripts/`, and in its `workflow/` its own decision log `workflow/adrs/`;
`packages/machinome-skills/` SHALL hold its manifest `pyproject.toml`, a
`README.md` that names its install line and the licence, its `MANIFEST.in`
and `.gitignore`, the links `LICENSE` and `LICENSES`, its package directory
`machinome/skills/` with its own `__init__.py` and none at `machinome/`, its
`tests/` and its `workflow/`, its specification being the framework's
`skills-distribution` and its history the set's. Their manual pages SHALL be
the framework's manual's.

Every distribution of the set but `machinome-mechanics` SHALL carry one
version, the set's, which `current_version` of the root's `.bumpversion.cfg`
declares, `machinome-viewer` included, whose Python package's
`__version__`, widget's `package.json` and entry in the root's npm lock SHALL
state it too, and every requirement between two of them SHALL be
the compatible-release pin `~=<version>`, in both directions, between the
framework and an extension package and between two extension packages alike
(`machinome-node-step` requires `machinome-node-cadquery`, and
`machinome-node-solid2` and `machinome-viewer-openscad` require
`machinome-node-openscad`).
`machinome-mechanics` SHALL carry its own version, the version of its
changelog's newest release section and of the manual's `mechanics_version`,
and a requirement between it and the framework SHALL be a floor (`>=`) that
the required distribution's version in the repository satisfies. The version
SHALL be bumped by the root `Makefile`'s `make bump` from that
configuration, which names every manifest's version but that of
`machinome-mechanics`, which it SHALL NOT name, every pin between the
distributions of the set and the files that restate the set's version, the
viewer's `__init__.py` and its widget's `package.json` among them; the
root's npm lock SHALL be brought to it by npm and `uv.lock` by uv.

The repository root SHALL hold the repository's record and tooling and no
distribution of its own: the licence texts (`LICENSE`, `LICENSES/`), the
contributor guide (`CONTRIBUTING.rst`), the AI-use statement (`AI-USE.md`),
the history (`HISTORY.rst`), `README.md`, which links every directory under
`packages/`, `context7.json`, the CI workflow under `.github/workflows/`,
`.bumpversion.cfg`, the `Makefile` of the repository's steps,
`scripts/check-dist`, the record of the campaigns that
span packages under `workflow/`, a `pyproject.toml` that declares a uv
workspace whose members are `packages/*`, naming every member as a workspace
source, with its `uv.lock`, and no `[project]` table, and a private
`package.json` that declares an npm workspace whose members are the
repository's JavaScript projects, today the viewer's widget, with the one
`package-lock.json` of the repository and no package of its own, its
`node_modules/` ignored. The workspace SHALL
install every member editable in compat mode, set at the root, and its
default `dev` group SHALL install the framework's `dev` extra. The CI SHALL
install the set from the lock with `uv sync --locked`.

The licence SHALL be stated once, at the root. The framework's directory
SHALL reach `LICENSE`, `LICENSES`, `HISTORY.rst`, `CONTRIBUTING.rst` and
`AI-USE.md` through relative symbolic links to the root's files, and the
framework's sdist and wheel SHALL carry them as regular files with the
root's contents, so the archives a release builds are the archives it
built before the layout.

`scripts/check-dist` SHALL build the sdist and the wheel of every member of
the workspace outside the repository, check them with `twine check
--strict`, install the wheels into a throwaway environment outside the
repository, an extension package through the framework's extra that
installs it and `machinome-mechanics`, `machinome-viewer` and
`machinome-skills` from their own
wheels, import and smoke each there, an engine through the framework's
seam that resolves it, a node package through its address and a viewer
through the framework's seam of viewers, rendering one
part on its kernel where its external program is available and building it as
far as the program allows where it is not, and upload nothing; the viewer's
source distribution builds its bundle with npm, which the script SHALL require
on the PATH before it builds; the CI SHALL run it through `make check` in a
`dist` job after its `test` and `docs` jobs, with Node installed.

#### Scenario: A contributor clones the repository

- **WHEN** a contributor clones `github.com/machinome/machinome`
- **THEN** the framework's `pyproject.toml`, `machinome/`, `tests/`,
  `docs/` and `openspec/` are under `packages/machinome/`, the engines'
  distributions under `packages/machinome-engine-brep/` and
  `packages/machinome-engine-mesh/`, the node packages' under
  `packages/machinome-node-cadquery/`, `-build123d/`, `-step/`, `-molejo/`,
  `-openscad/`, `-solid2/`, `-jscad/`, `-stl/` and `-freecad/`, the
  mechanics helpers' with their tests and records under
  `packages/machinome-mechanics/`, the browser viewer's with its widget,
  tests and records under `packages/machinome-viewer/`, the skills package's
  with its tests and working record under `packages/machinome-skills/`, and
  the root holds the repository's record, the uv and npm workspace manifests
  and their locks, and none of the framework's sources

#### Scenario: The licence is reached from the package directory

- **WHEN** `packages/machinome/LICENSE`, `LICENSES`, `HISTORY.rst`,
  `CONTRIBUTING.rst` or `AI-USE.md` is read
- **THEN** it is a relative symbolic link resolving to the root's file of
  the same name, and the layout test fails naming the entry if it is a
  copy or resolves elsewhere

#### Scenario: An extension package carries only what distinguishes it

- **WHEN** the files of an extension package's directory are listed, ignored
  build leavings excepted
- **THEN** they are `pyproject.toml`, `README.md`, the links `LICENSE` and
  `LICENSES` to the root's, and the module at its address, such as
  `machinome/engine/brep.py` of `packages/machinome-engine-brep/` or
  `machinome/node/step.py` of `packages/machinome-node-step/`, or the package
  directory `machinome/node/openscad/` with its five modules for
  `packages/machinome-node-openscad/`, or `machinome/node/freecad/` with its
  four modules for `packages/machinome-node-freecad/`, and the layout test
  fails naming any other entry or an `__init__.py` other than that package's
  own

#### Scenario: Every sibling is an extension package of the table

- **WHEN** a directory `packages/machinome-<name>/` exists that neither the
  layout test's table of extension packages nor its table of products lists
- **THEN** the layout test fails naming the directory

#### Scenario: The set carries one version

- **WHEN** the manifests under `packages/` and the root's `.bumpversion.cfg`
  are read
- **THEN** every manifest's version but `machinome-mechanics`'s equals
  `.bumpversion.cfg`'s `current_version`, the framework's included, every
  requirement between two distributions of the set is `~=` that version,
  `.bumpversion.cfg` names every manifest but `machinome-mechanics`'s, the
  viewer's `__init__.py`, its widget's `package.json` and the root npm lock's
  entry for it state the same version, and the framework's `setup.cfg` holds
  no version table

#### Scenario: The archives carry the licence

- **WHEN** `scripts/check-dist` builds the framework from
  `packages/machinome/` and each extension package from its directory
- **THEN** each sdist holds its linked entries as regular files whose
  bytes equal the root's, each wheel's metadata holds the licence texts
  under its `licenses/` directory, each installed distribution states
  `GPL-2.0-or-later OR CERN-OHL-S-2.0+`, and nothing is uploaded

#### Scenario: The extension packages are smoked through the framework

- **WHEN** `scripts/check-dist` installs the built wheels
- **THEN** it installs `machinome-engine-brep` and `machinome-engine-mesh`
  through the framework's `brep` and `mesh` extras from the built archives,
  resolves each provider through its seam, finds its file owned by its own
  distribution, runs one operation on its kernel, and finds its version
  equal to the framework's

#### Scenario: The node packages are smoked through the framework

- **WHEN** `scripts/check-dist` installs the built wheels
- **THEN** it installs `machinome-node-cadquery`, `machinome-node-build123d`,
  `machinome-node-step` and `machinome-node-molejo` through the framework's
  `cadquery`, `build123d`, `step` and `molejo` extras from the built
  archives, imports each module at its address, finds its file owned by its
  own distribution and its version equal to the framework's, and renders one
  part on its kernel whose volume the B-rep engine reads

#### Scenario: A developer syncs the workspace

- **WHEN** `uv sync` runs at the repository root
- **THEN** the framework and its extension packages are installed editable
  in compat mode from their directories, the framework with its `dev`
  extra, `machinome.engine.brep` resolves from
  `packages/machinome-engine-brep/`, `machinome.node.step` from
  `packages/machinome-node-step/`, `machinome.mechanics` from
  `packages/machinome-mechanics/`, `machinome.viewer.web` from
  `packages/machinome-viewer/`, `machinome.skills` from
  `packages/machinome-skills/`, and the suite runs from
  `packages/machinome/`

#### Scenario: The root manifest declares a distribution

- **WHEN** the root `pyproject.toml` gains a `[project]` table, or its
  workspace stops naming `packages/*`, or a directory under `packages/` is
  not one of its sources
- **THEN** the layout test fails naming the table or the directory

#### Scenario: The node packages over no B-rep engine are smoked through the framework

- **WHEN** `scripts/check-dist` installs the built wheels
- **THEN** it installs `machinome-node-openscad`, `machinome-node-solid2`,
  `machinome-node-jscad` and `machinome-node-stl` through the framework's
  `openscad`, `solid2`, `jscad` and `stl` extras from the built archives,
  imports each module at its address, finds the files it ships owned by its
  own distribution and its version equal to the framework's, renders an
  `OpenScadNode` and a `Solid2Node` part through OpenSCAD where the binary is
  on the PATH and writes their SCAD where it is not, renders an `StlNode`
  part, and constructs a `JScadNode` part, and finds no viewer module in the
  OpenSCAD node package's distribution

#### Scenario: The OpenSCAD viewer is smoked through the framework

- **WHEN** `scripts/check-dist` installs the built wheels
- **THEN** it installs `machinome-viewer-openscad` through the framework's
  `viewer-openscad` extra from the built archives, finds its one module
  `machinome/viewer/openscad/__init__.py` owned by its own distribution and
  its version and pins the framework's, resolves it through
  `machinome.viewer.viewer('openscad')` to that file with the seam's contract
  version and the operations `present` and `capture`, and draws a still of an
  `OpenScadNode` part through OpenSCAD where the binary is on the PATH and
  presents and withdraws its SCAD where it is not

#### Scenario: The FreeCAD node package is smoked through the framework

- **WHEN** `scripts/check-dist` installs the built wheels
- **THEN** it installs `machinome-node-freecad` through the framework's
  `freecad` extra from the built archives, imports `machinome.node.freecad`
  at its address, finds the four files it ships owned by its own distribution
  and its version equal to the framework's, declares a
  `FreeCADAssemblyNode` subclass over a synthetic fixture, and constructs and
  runs it to its enabled limit where `MACHINOME_FREECAD_ROOT` is set, and
  finds its construction refused naming `MACHINOME_FREECAD_ROOT` where it is
  not

#### Scenario: A product keeps its record in its directory

- **WHEN** the entries of `packages/machinome-mechanics/` are listed, ignored
  build leavings excepted
- **THEN** they are `pyproject.toml`, `README.md`, `CHANGELOG.md`,
  `MANIFEST.in`, `.gitignore`, the links `LICENSE` and `LICENSES` to the
  root's, `machinome/` holding the package directory `mechanics/` with its own
  `__init__.py`, `tests/`, `openspec/` and `workflow/`, its manifest states
  `GPL-2.0-or-later OR CERN-OHL-S-2.0+` and the root's licence files, and the
  layout test fails naming any other entry or an `__init__.py` at
  `machinome/`

#### Scenario: The mechanics helpers carry their own version

- **WHEN** the manifest of `machinome-mechanics`, its `CHANGELOG.md`, the
  manual's `mechanics_version`, the framework's `mechanics` extra and
  `.bumpversion.cfg` are read
- **THEN** the manifest's version equals the changelog's newest release
  section's and `mechanics_version`, the extra and the package's requirement
  on the framework are floors the versions in the repository satisfy, and no
  table of `.bumpversion.cfg` names the manifest

#### Scenario: The mechanics package is smoked from its wheel

- **WHEN** `scripts/check-dist` installs the built wheels
- **THEN** it installs `machinome-mechanics` from its own wheel by path,
  imports `machinome.mechanics`, finds its ten modules owned by its own
  distribution inside the throwaway environment, its version its own, its
  requirement `machinome>=0.8.0` and the framework's `mechanics` extra
  naming it, computes a pose numerically and a deferred expression from the
  framework's animation time, and finds its licence texts

#### Scenario: The viewer keeps its record in its directory

- **WHEN** the entries of `packages/machinome-viewer/` are listed, ignored
  build leavings excepted
- **THEN** they are `pyproject.toml`, `README.md`, `CHANGELOG.md`,
  `MANIFEST.in`, `.gitignore`, the links `LICENSE` and `LICENSES` to the
  root's, `machinome/` holding the package directory `viewer/web/` with its
  own `__init__.py` and the widget, `scripts/`, `tests/`, `openspec/` and
  `workflow/`, its manifest states `GPL-2.0-or-later OR CERN-OHL-S-2.0+` and
  the root's licence files, and the layout test fails naming any other entry
  or an `__init__.py` at `machinome/` or `machinome/viewer/`

#### Scenario: The npm workspace installs the widget at the root

- **WHEN** a contributor runs `npm ci` at the repository root
- **THEN** the dependencies of every member of the root `package.json`'s
  workspace are installed in the root's `node_modules/` from the root's
  `package-lock.json`, the one lockfile of the repository, and the widget's
  bundle builds with `npm run build` from the root or the widget's directory

#### Scenario: The viewer is smoked from its wheel

- **WHEN** `scripts/check-dist` installs the built wheels
- **THEN** it installs `machinome-viewer` from its own wheel by path, imports
  its package, finds its ten modules and its built bundle owned by its own
  distribution inside the throwaway environment and no widget source, its
  version and its pin the framework's, the framework's `viewer` and
  `web-snapshot` extras pinning it, no entry point in the group
  `machinome.viewer`, the provider the seam resolves for `web` being its
  `__init__.py` with the seam's contract version and the operations
  `present`, `capture`, `serve` and `embed`, its report naming the installed
  bundle, the widget's API and document versions,
  a banner stating the version, the API, the set's licence expression and the
  repository, and its licence texts; the distribution declares no entry point
  in the group `console_scripts` and the environment holds no
  `machinome-viewer` executable; `machinome viewer`, `machinome viewer
  describe` and `python -m machinome.viewer.web describe` exit zero

#### Scenario: The skills package keeps its tests and working record

- **WHEN** the entries of `packages/machinome-skills/` are listed, ignored
  build leavings excepted
- **THEN** they are `pyproject.toml`, `README.md`, `MANIFEST.in`,
  `.gitignore`, the links `LICENSE` and `LICENSES` to the root's,
  `machinome/` holding the package directory `skills/` with its own
  `__init__.py`, `tests/` and `workflow/`, its manifest states
  `GPL-2.0-or-later OR CERN-OHL-S-2.0+` and the root's licence files, its
  version is the framework's, its requirement on the framework and the
  framework's `skills` extra are `~=` that version, `.bumpversion.cfg` names
  its manifest, and the layout test fails naming any other entry

#### Scenario: The skills package is smoked from its wheel

- **WHEN** `scripts/check-dist` installs the built wheels
- **THEN** it installs `machinome-skills` from its own wheel by path, imports
  `machinome.skills`, finds its modules, its registry and the two skills
  owned by its own distribution inside the throwaway environment, its version
  the framework's, its requirement `machinome~=<version>`, the framework's
  `skills` extra naming it and its entry `skills` in `machinome.commands`,
  runs `machinome skills install --tools agents,claude` into a new directory
  and reads the eight files back, each `SKILL.md` with the marker, and finds
  its licence texts
