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
`machinome-node-openscad`, `machinome-node-solid2`, `machinome-node-jscad` and
`machinome-node-stl`, SHALL each be such a sibling, holding only its
manifest `pyproject.toml`, a `README.md` that names its install line and the
licence, the relative symbolic links `LICENSE` and `LICENSES` to the root's,
and its namespace portion at its address under `machinome/`, with no
`__init__.py` at the levels the framework's import package defines; a portion
that is a package directory, `machinome/node/openscad/`, holds its own
`__init__.py` at its address, below those levels, and its manifest's package
search names that package. Its specs, tests, decision records and manual pages
SHALL be the framework's.
Every distribution of the set SHALL carry one version, the framework's, and
every requirement between two of them SHALL be the compatible-release pin
`~=<version>`, in both directions, between the framework and an extension
package and between two extension packages alike (`machinome-node-step`
requires `machinome-node-cadquery`, and `machinome-node-solid2` requires
`machinome-node-openscad`). The version SHALL be bumped from one
configuration at the repository root, `.bumpversion.cfg`, naming every
manifest's version, every pin between the distributions and the files that
restate the framework's version.

The repository root SHALL hold the repository's record and tooling and no
distribution of its own: the licence texts (`LICENSE`, `LICENSES/`), the
contributor guide (`CONTRIBUTING.rst`), the AI-use statement (`AI-USE.md`),
the history (`HISTORY.rst`), `README.md`, which links every directory under
`packages/`, `context7.json`, the CI workflow under `.github/workflows/`,
`.bumpversion.cfg`, `scripts/check-dist`, the record of the campaigns that
span packages under `workflow/`, and a `pyproject.toml` that declares a uv
workspace whose members are `packages/*`, naming every member as a workspace
source, with its `uv.lock`, and no `[project]` table. The workspace SHALL
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
installs it, import and smoke each there, an engine through the framework's
seam that resolves it and a node package through its address, rendering one
part on its kernel where its external program is available and building it as
far as the program allows where it is not, and upload nothing; the CI SHALL
run it
in a `dist` job after its `test` and `docs` jobs.

#### Scenario: A contributor clones the repository

- **WHEN** a contributor clones `github.com/machinome/machinome`
- **THEN** the framework's `pyproject.toml`, `machinome/`, `tests/`,
  `docs/` and `openspec/` are under `packages/machinome/`, the engines'
  distributions under `packages/machinome-engine-brep/` and
  `packages/machinome-engine-mesh/`, the node packages' under
  `packages/machinome-node-cadquery/`, `-build123d/`, `-step/`, `-molejo/`,
  `-openscad/`, `-solid2/`, `-jscad/` and `-stl/`, and the root holds the
  repository's
  record, the workspace manifest and its lock, and none of the framework's
  sources

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
  `packages/machinome-node-openscad/`, and the layout test fails naming any
  other entry or an `__init__.py` other than that package's own

#### Scenario: Every sibling is an extension package of the table

- **WHEN** a directory `packages/machinome-<name>/` exists that the layout
  test's table of extension packages does not list
- **THEN** the layout test fails naming the directory

#### Scenario: The set carries one version

- **WHEN** the manifests under `packages/` and the root's `.bumpversion.cfg`
  are read
- **THEN** every manifest's version and `.bumpversion.cfg`'s
  `current_version` equal the framework's, every requirement between two
  distributions of the set is `~=` that version, `.bumpversion.cfg` names
  every manifest, and the framework's `setup.cfg` holds no version table

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
  `packages/machinome-node-step/`, and the suite runs from
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
  part, constructs a `JScadNode` part, and resolves the OpenSCAD renderer
  through the table of supported node types to that distribution's file
