## MODIFIED Requirements

### Requirement: Extras select independent Machinome products

The distribution SHALL expose `viewer`, `mechanics`, `skills`, `movie` and
`studio` extras that select `machinome-viewer`, `machinome-mechanics`,
`machinome-skills`, `machinome-movie` and `machinome-studio` respectively.
The default framework installation SHALL depend on none of them.
`machinome-mechanics` is a distribution of the repository, at
`packages/machinome-mechanics/`, whose package `machinome.mechanics` the
framework never imports; the `mechanics` extra SHALL require it at a floor
that its version in the repository satisfies. `machinome-viewer` is a
distribution of the repository, at `packages/machinome-viewer/`, numbered with
the framework, which the framework finds through its entry point and runs as
a separate process. `machinome-skills` is a distribution of the repository, at
`packages/machinome-skills/`, whose package `machinome.skills` the framework
never imports; the `skills` extra SHALL require it with the compatible-release
pin `~=<version>`, the version being the framework's own. `machinome-movie` is
a distribution of the repository, at `packages/machinome-movie/`, whose
package `machinome.movie` the framework never imports; the `movie` extra
SHALL require it with the compatible-release pin `~=<version>`, the version
being the framework's own.
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

- **WHEN** the `viewer`, `mechanics`, `skills`, `movie` or `studio` extra
  states its one requirement with an extras bracket or a version floor
- **THEN** that requirement's name is still `machinome-viewer`,
  `machinome-mechanics`, `machinome-skills`, `machinome-movie` or
  `machinome-studio` respectively, and the identity check reads the name, so
  a floor neither breaks it nor hides a renamed product

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

#### Scenario: A user installs the movie extra

- **WHEN** `pip install "machinome[movie]"` resolves the framework's
  distributions
- **THEN** the `machinome-movie` distribution of the repository, numbered with
  the framework, is installed with the viewer it requires, and `machinome
  movie` is a command of `machinome`, without the framework importing
  `machinome.movie`

#### Scenario: A reader asks for the studio extra before publication

- **WHEN** current 0.7 guidance shows `pip install "machinome[studio]"`
- **THEN** it also states that the installation cannot resolve from an index
  until Machinome Studio is published

## ADDED Requirements

### Requirement: The films are a product of the set and a member of the npm workspace

The distribution `machinome-movie` SHALL be a product of the repository that
keeps its record in its directory: `packages/machinome-movie/` SHALL hold its
manifest `pyproject.toml`, a `README.md` that names its install lines and the
licence, its `CHANGELOG.md`, its `MANIFEST.in` and `.gitignore`, the relative
symbolic links `LICENSE` and `LICENSES` to the root's, its package directory
`machinome/movie/` with its own `__init__.py` and none at `machinome/`, its
`tests/`, its `openspec/`, its `workflow/` (its decision log under
`workflow/adrs/`) and its `experiments/`. Its manual pages SHALL be the
framework's manual's.

It SHALL carry the framework's version and require the framework and the
browser viewer with the compatible-release pin `~=<version>`; the root's
`.bumpversion.cfg` SHALL name its manifest's version, its pins and the version
of its JavaScript directory's `package.json`, and the release records SHALL
hold that `package.json`, its own lock and the root lock's entry for it to the
set's version.

Its JavaScript directory, `packages/machinome-movie/machinome/movie/js/`,
SHALL be the second member of the root's npm workspace, after the viewer's
widget, under the name `@machinome/movie`, private. The root SHALL hold an
`.npmrc` that installs each member's direct dependencies in that member's own
`node_modules`, and one `package-lock.json`, and the movie's directory SHALL
keep a `package-lock.json` of its own, from which an installed copy installs
its dependencies; both locks SHALL list exactly the dependencies and versions
its `package.json` declares. No `node_modules` SHALL be tracked.

`scripts/check-dist` SHALL install the movie's wheel by its path, find its
files, its version, its pins, the extra's requirement in the framework's
metadata and its entry point in `machinome.commands`, run `machinome movie
setup` in the throwaway environment, run one verb of the Node side, and remove
the Node dependencies with `machinome movie setup --remove`; it SHALL refuse
before building when the movie is a member and Node or npm is not on the PATH.

#### Scenario: The movie's directory holds its package and its record

- **WHEN** the entries of `packages/machinome-movie/` are listed, ignored
  leavings excepted
- **THEN** they are those named above, `LICENSE` and `LICENSES` link the
  root's, `machinome/movie/__init__.py` is a file and `machinome/__init__.py`
  is absent, and the layout test fails naming any other entry

#### Scenario: The workspace installs the movie's packages beside it

- **WHEN** `npm ci` runs at the repository root
- **THEN** the viewer's widget and the movie's directory are both installed,
  the movie's direct dependencies in
  `packages/machinome-movie/machinome/movie/js/node_modules/`, and the
  viewer's resolutions are those its own join locked

#### Scenario: The movie's two locks agree with its manifest

- **WHEN** the movie's `package.json` gains a dependency, or changes one's
  version, and only one lock is regenerated
- **THEN** a test fails naming the lock that disagrees and the dependency

#### Scenario: The wheel is smoked as a user installs it

- **WHEN** `scripts/check-dist` installs the movie's wheel beside the
  framework's and the viewer's
- **THEN** `machinome movie review` refuses naming `machinome movie setup`,
  `machinome movie setup` installs the Node dependencies into the installed
  package's `js/node_modules`, the same verb then reaches Node, and `setup
  --remove` leaves no `node_modules` behind
