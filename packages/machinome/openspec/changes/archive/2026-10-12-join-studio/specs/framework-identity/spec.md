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
being the framework's own. `machinome-studio` is a distribution of the
repository, at `packages/machinome-studio/`, whose package `machinome.studio`
the framework never imports; the `studio` extra SHALL require it with the
compatible-release pin `~=<version>`, the version being the framework's own.
Current release material SHALL NOT state that the `studio` extra cannot
resolve; until the set's next release is published, the status page SHALL
state that no index serves `machinome-studio` yet.

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

#### Scenario: A user installs the studio extra

- **WHEN** `pip install "machinome[studio]"` resolves the framework's
  distributions
- **THEN** the `machinome-studio` distribution of the repository, numbered
  with the framework, is installed with the viewer and its capture, and
  `machinome studio` is a command of `machinome`, without the framework
  importing `machinome.studio`

#### Scenario: A reader asks for the studio extra before publication

- **WHEN** current guidance shows `pip install "machinome[studio]"` while no
  index serves the set's release that includes the studio
- **THEN** the status page says no index serves `machinome-studio` yet, no
  other page says the extra cannot resolve, and the extra pins `~=` the
  framework's version, a test failing naming the extra if it does not

## ADDED Requirements

### Requirement: The studio is a product of the set and the third member of the npm workspace

The distribution `machinome-studio` SHALL be a product of the repository that
keeps its record in its directory: `packages/machinome-studio/` SHALL hold its
manifest `pyproject.toml`, a `README.md` that names its install lines and the
licence, its `CHANGELOG.md`, its `MANIFEST.in` and `.gitignore`, the relative
symbolic links `LICENSE` and `LICENSES` to the root's, its package directory
`machinome/studio/` with its own `__init__.py` and none at `machinome/`, its
`scripts/`, its `tests/`, its `openspec/` and its `workflow/` (its decision
log under `workflow/adrs/`, its architecture overview, design reference,
product records and spikes). Its manual pages SHALL be the framework's
manual's. No module or alias of its former package name `floor` SHALL be
shipped.

It SHALL carry the framework's version and require the framework and the
browser viewer with its capture with the compatible-release pin
`~=<version>`; the root's `.bumpversion.cfg` SHALL name its manifest's
version, its pins and the version of its frontend's `package.json`, and the
release records SHALL hold that `package.json` and the root lock's entry for
it to the set's version.

Its frontend, `packages/machinome-studio/machinome/studio/frontend/`, SHALL be
the third member of the root's npm workspace, after the viewer's widget and
the movie's directory, under the name `@machinome/studio`, private, with no
lockfile of its own; the root lock SHALL hold its resolutions, installed in
its own `node_modules`. Its built browser surface,
`packages/machinome-studio/machinome/studio/static/`, SHALL NOT be tracked.

`scripts/check-dist` SHALL install the studio's wheel by its path, find its
modules, its built surface and its skills owned by its distribution inside the
throwaway environment and no frontend source, its version, its pins, the
extra's requirement in the framework's metadata and its entry point in
`machinome.commands`, load both of its profiles from the installed package,
start `machinome studio` on a scratch catalogue and read its hub's page, and
stop it; it SHALL refuse before building when the studio is a member and npm
is not on the PATH.

#### Scenario: The studio's directory holds its package and its record

- **WHEN** the entries of `packages/machinome-studio/` are listed, ignored
  leavings excepted
- **THEN** they are those named above, `LICENSE` and `LICENSES` link the
  root's, `machinome/studio/__init__.py` is a file and `machinome/__init__.py`
  is absent, its manifest states `GPL-2.0-or-later OR CERN-OHL-S-2.0+`, and
  the layout test fails naming any other entry

#### Scenario: The workspace installs the studio's frontend beside it

- **WHEN** `npm ci` runs at the repository root
- **THEN** the studio's frontend is installed with its direct dependencies in
  its own `node_modules`, the widget's and the movie's resolutions are those
  their joins locked, and the frontend builds its surface from the root

#### Scenario: The frontend keeps no lock of its own

- **WHEN** the tracked files are listed
- **THEN** no `package-lock.json` is under the studio's directory, and the
  layout test fails naming one that is

#### Scenario: The studio's wheel is smoked as a maker installs it

- **WHEN** `scripts/check-dist` installs the studio's wheel beside the
  framework's and the viewer's
- **THEN** both profiles load from the installed package, the builder's
  skills including `machinome-simulate`, `machinome studio` prints its
  address, its hub answers with the studio's page, and the process is stopped
