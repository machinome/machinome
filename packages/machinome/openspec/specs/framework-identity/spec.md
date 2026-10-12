# framework-identity Specification

## Purpose
TBD - created by archiving change rename-framework-to-machinome. Update Purpose after archive.
## Requirements
### Requirement: The framework has one Machinome identity

The framework distribution SHALL be named `machinome`, its import package
SHALL be `machinome`, its executable SHALL be `machinome`, and its source
repository SHALL be `machinome/machinome`. Current product metadata,
documentation, diagnostics, templates and integration contracts SHALL use
those names.

#### Scenario: A user installs and imports the framework

- **WHEN** a user installs `machinome`
- **THEN** the framework is importable as `machinome`
- **AND** its command is available as `machinome`

#### Scenario: A reader follows the source link

- **WHEN** current package metadata or documentation names the source
  repository
- **THEN** it points to `github.com/machinome/machinome`

### Requirement: Version 0.7 records the rename lineage

The first Machinome release SHALL be version 0.7.0 and SHALL state that it is
the direct continuation of solid-node 0.6.0 with the repository's complete Git
history. Its changelog, release note and migration guidance SHALL explain the
reason for the name change and map old distribution, import, command,
configuration, viewer and mechanics names to their Machinome replacements.
A later 0.7.x release SHALL keep that material and add its own changelog
entry, `HISTORY.rst` entry and release-note section above it.

Historical ADRs, archived changes and release records SHALL retain the names
that were true when they were written. Current synthesis and indexes SHALL
make the transition discoverable.

#### Scenario: A 0.6 user reads the 0.7 release material

- **WHEN** the user looks for the next release after solid-node 0.6.0
- **THEN** the material identifies Machinome 0.7.0 as that release and gives
  the complete migration map

#### Scenario: A 0.7.0 user reads the 0.7.1 release material

- **WHEN** the user looks for what changed after Machinome 0.7.0
- **THEN** the changelog's 0.7.1 entry sits above the 0.7.0 entry, and the
  rename and migration material of 0.7.0 is unchanged beneath it

#### Scenario: A reader opens a historical decision

- **WHEN** an ADR predating 0.7 discusses solid-node
- **THEN** its historical wording remains intact and current architecture
  material identifies it as a decision inherited by Machinome

### Requirement: The renamed runtime is a clean break

Machinome 0.7 SHALL NOT install a `solid_node` import package or a `solid`
console alias. It SHALL read project configuration from `[tool.machinome]` and
runtime settings from `MACHINOME_*` names. When it can identify a former
`[tool.solid-node]` table or former environment name, it SHALL fail with a
migration message rather than silently ignoring configuration or running with
different defaults.

#### Scenario: A project uses current configuration

- **WHEN** a project declares models under `[tool.machinome]`
- **THEN** `machinome models`, `machinome build --all`, and `machinome test
  --all` resolve those models

#### Scenario: A project retains the former table

- **WHEN** a project contains `[tool.solid-node]` and no `[tool.machinome]`
- **THEN** the command fails naming the table and its `[tool.machinome]`
  replacement

#### Scenario: A caller imports the former package

- **WHEN** only Machinome 0.7 is installed and a caller imports `solid_node`
- **THEN** no compatibility package supplied by Machinome satisfies that import

### Requirement: Extras select independent Machinome products

The distribution SHALL expose `viewer`, `mechanics`, `skills` and `studio`
extras that select `machinome-viewer`, `machinome-mechanics`,
`machinome-skills` and `machinome-studio` respectively. The default framework
installation SHALL depend on none of them.
`machinome-mechanics` is a distribution of the repository, at
`packages/machinome-mechanics/`, whose package `machinome.mechanics` the
framework never imports; the `mechanics` extra SHALL require it at a floor
that its version in the repository satisfies. `machinome-viewer` is a
distribution of the repository, at `packages/machinome-viewer/`, numbered with
the framework, which the framework finds through its entry point and runs as
a separate process. `machinome-skills` is a distribution of the repository,
at `packages/machinome-skills/`, whose package `machinome.skills` the
framework never imports; the `skills` extra SHALL require it with the
compatible-release pin `~=<version>`, the version being the framework's own.
Current release material SHALL state that the experimental studio remains
unpublished and that the `studio` extra cannot resolve from a package index
until that publication occurs.

The `viewer` extra and the `web-snapshot` extra SHALL require the viewer of
the framework's own release with the compatible-release pin the set's
distributions state between each other, `machinome-viewer~=<version>` and
`machinome-viewer[snapshot]~=<version>`, and the matching viewer version the
manual declares in its release facts SHALL be that version, so a release that
moves the set moves both pins with it or fails naming the extra left behind.
The pin states what the extra installs, not what a document needs: the
framework SHALL keep reading the installed viewer's own report for what it
renders, and current upgrade material SHALL keep stating which older viewers
read the documents the release exports.

#### Scenario: A user installs the viewer extra

- **WHEN** `pip install "machinome[viewer]"` resolves from published packages
- **THEN** the `machinome-viewer` distribution of the repository, released
  with the framework, is installed beside it

#### Scenario: A user upgrades the framework with the viewer extra

- **WHEN** an installation holding an older viewer runs
  `pip install -U "machinome[viewer]"` against published packages
- **THEN** the viewer is upgraded to the release of the framework it is
  installed beside

#### Scenario: The floor and the declared matching viewer agree

- **WHEN** the release facts declare the matching viewer version
- **THEN** it is the framework's version, the `viewer` and `web-snapshot`
  extras each pin `~=` exactly that version, and a test fails naming the
  extra whose pin differs

#### Scenario: The extras keep the Machinome name under a version floor

- **WHEN** the `viewer`, `mechanics`, `skills` or `studio` extra states its
  one requirement with an extras bracket or a version floor
- **THEN** that requirement's name is still `machinome-viewer`,
  `machinome-mechanics`, `machinome-skills` or `machinome-studio`
  respectively, and the identity check reads the name, so a floor neither
  breaks it nor hides a renamed product

#### Scenario: A user installs the mechanics extra

- **WHEN** `pip install "machinome[mechanics]"` resolves from published
  packages
- **THEN** the `machinome-mechanics` distribution of the repository is
  installed, its helpers imported from `machinome.mechanics`, without the
  framework importing or re-exporting them

#### Scenario: A user installs the skills extra

- **WHEN** `pip install "machinome[skills]"` resolves the framework's
  distributions
- **THEN** the `machinome-skills` distribution of the repository, numbered
  with the framework, is installed, and `machinome skills` is a command of
  `machinome`, without the framework importing `machinome.skills`

#### Scenario: A reader asks for the studio extra before publication

- **WHEN** current 0.7 guidance shows `pip install "machinome[studio]"`
- **THEN** it also states that the installation cannot resolve from an index
  until Machinome Studio is published

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
`machinome-node-stl` and `machinome-node-freecad`, SHALL each be such a
sibling, holding only its
manifest `pyproject.toml`, a `README.md` that names its install line and the
licence, the relative symbolic links `LICENSE` and `LICENSES` to the root's,
and its namespace portion at its address under `machinome/`, with no
`__init__.py` at the levels the framework's import package defines; a portion
that is a package directory, `machinome/node/openscad/` or
`machinome/node/freecad/`, holds its own `__init__.py` at its address, below
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
version, the framework's, `machinome-viewer` included, whose Python package's
`__version__`, widget's `package.json` and entry in the root's npm lock SHALL
state it too, and every requirement between two of them SHALL be
the compatible-release pin `~=<version>`, in both directions, between the
framework and an extension package and between two extension packages alike
(`machinome-node-step` requires `machinome-node-cadquery`, and
`machinome-node-solid2` requires `machinome-node-openscad`).
`machinome-mechanics` SHALL carry its own version, the version of its
changelog's newest release section and of the manual's `mechanics_version`,
and a requirement between it and the framework SHALL be a floor (`>=`) that
the required distribution's version in the repository satisfies. The version
SHALL be bumped from one configuration at the repository root,
`.bumpversion.cfg`, naming every manifest's version but that of
`machinome-mechanics`, which it SHALL NOT name, every pin between the
distributions of the set and the files that restate the framework's version,
the viewer's `__init__.py` and its widget's `package.json` among them; the
root's npm lock SHALL be brought to it by npm.

The repository root SHALL hold the repository's record and tooling and no
distribution of its own: the licence texts (`LICENSE`, `LICENSES/`), the
contributor guide (`CONTRIBUTING.rst`), the AI-use statement (`AI-USE.md`),
the history (`HISTORY.rst`), `README.md`, which links every directory under
`packages/`, `context7.json`, the CI workflow under `.github/workflows/`,
`.bumpversion.cfg`, `scripts/check-dist`, the record of the campaigns that
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
seam that resolves it and a node package through its address, rendering one
part on its kernel where its external program is available and building it as
far as the program allows where it is not, and upload nothing; the viewer's
source distribution builds its bundle with npm, which the script SHALL require
on the PATH before it builds; the CI SHALL run it in a `dist` job after its
`test` and `docs` jobs, with Node installed.

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
- **THEN** every manifest's version but `machinome-mechanics`'s and
  `.bumpversion.cfg`'s `current_version` equal the framework's, every
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
  part, constructs a `JScadNode` part, and resolves the OpenSCAD renderer
  through the table of supported node types to that distribution's file

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
  its package, finds its eight modules and its built bundle owned by its own
  distribution inside the throwaway environment and no widget source, its
  version and its pin the framework's, the framework's `viewer` and
  `web-snapshot` extras pinning it, the `machinome.viewer` entry point's
  report naming the installed bundle, the widget's API and document versions,
  a banner stating the version, the API, the set's licence expression and the
  repository, and its licence texts; `machinome-viewer describe` and
  `machinome viewer` exit zero

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

