## ADDED Requirements

### Requirement: The 0.8.1 release is recorded

The release facts of Machinome 0.8.1 SHALL agree wherever they are
stated, by the same rules as 0.8.0's: the five version files hold the
version `pyproject.toml` states, and `docs/conf.py`'s release block states
the release date, 10 October 2026, the matching viewer 0.8.1, viewer API
29 and document versions 1 to 13. The `viewer` and `web-snapshot` extras
SHALL require `machinome-viewer` 0.8.1 or newer. The changelog's first
release section SHALL be `Machinome 0.8.1`, dated `Released on
10/Oct/2026`, with no `Unreleased` section, opening with what a maker gets
and sending a reader to the upgrading page for the changes a project may
have to follow. `HISTORY.rst`'s top entry SHALL be
`Machinome 0.8.1 (2026-10-10)`. `docs/releases/release-0.8.rst` SHALL end
with a section naming 0.8.1 and dated 10 October 2026. `context7.json`
SHALL state 0.8.1, its date and the matching viewer 0.8.1, API 29. The
upgrading page SHALL open with a part for upgrading from 0.8.0 to 0.8.1,
above the 0.7 to 0.8 part, which stays intact.

#### Scenario: A reader checks which version the manual describes

- **WHEN** a reader compares the installed package's version with the
  manual's status page, changelog and history
- **THEN** all state 0.8.1, released on 10 October 2026, and the
  changelog's first release section is the 0.8.1 section

#### Scenario: A 0.8.0 user upgrades

- **WHEN** a 0.8.0 user opens the upgrading page
- **THEN** its first part names each change since 0.8.0 a project may
  have to follow, with what to change

#### Scenario: A maker installs the viewer extra

- **WHEN** a maker installs `machinome[viewer]` 0.8.1
- **THEN** the requirement names `machinome-viewer>=0.8.1`, the viewer
  the manual declares as matching

## MODIFIED Requirements

### Requirement: The 0.8.0 release is recorded

The release facts of Machinome 0.8.0 SHALL agree wherever they are
stated. `pyproject.toml`, `machinome/__init__.py`,
`machinome/vet/universe.toml`, `setup.cfg`'s bumpversion table and
`docs/conf.py`'s `release` SHALL all state the released version, and the
tests SHALL hold them to the version `pyproject.toml` states rather than
to a literal. `docs/conf.py`'s release block SHALL be the one place the
manual states the release date, the matching viewer's version and API,
the document versions, the mechanics version and the framework's
licence; a page SHALL state each through its substitution
(`|release_date|`, `|viewer_version|`, `|viewer_api|`,
`|document_versions|`, `|mechanics_version|`, `|framework_licence|`),
never as a literal.

The framework's licence SHALL be stated as GPL-2.0-or-later or
CERN-OHL-S-2.0-or-later, at the recipient's choice, as the current fact
and nothing more: no comparison with any other licence, no position on
derivative works, no exception and no reason. The framework's licence
SHALL reach a page only through the one fact in `docs/conf.py`,
`|framework_licence|`, and `README.rst` SHALL state the same words. No
`.rst` page under `docs/` other than the historical release notes under
`docs/releases/` SHALL spell a licence identifier literally but the
viewer's `AGPL-3.0-or-later`; `README.rst` SHALL spell no licence
identifier but `AGPL-3.0-or-later` and the exact words of `docs/conf.py`'s
`framework_licence`. The browser viewer SHALL be stated as the separate
AGPL-3.0-or-later package.

The changelog SHALL keep a `Machinome 0.8.0` section, dated
`Released on 05/Oct/2026`, below any later release's; it SHALL open with
what a maker gets, state the licence first, and list every breaking
change of 0.8 in one line each with a link to the upgrading page.
`HISTORY.rst` SHALL keep the entry `Machinome 0.8.0 (2026-10-05)`.
`docs/releases/release-0.8.rst` SHALL be the release note of the 0.8
line, its title naming 0.8 and dated 5 October 2026, reached from the
changelog. The upgrading page SHALL keep a part for upgrading from 0.7 to
0.8 that lists every breaking change of 0.8 and, for each, what to
change, above the 0.6 to 0.7 material, which stays intact; no section of
it SHALL be marked unreleased or speak of "the next release".

#### Scenario: A reader checks which version the manual describes

- **WHEN** a reader reads the changelog and the history after a later
  release
- **THEN** the 0.8.0 section and history entry still state 0.8.0,
  released on 5 October 2026, below the later release's

#### Scenario: A version file is left behind

- **WHEN** one of the files that state the version is moved and another
  is not
- **THEN** the release-records test fails naming the file that disagrees
  with `pyproject.toml`

#### Scenario: A reader looks up the licence

- **WHEN** a reader reads the installation page, the "why" page, the
  status page or the README
- **THEN** each states the framework's licence as GPL-2.0-or-later or
  CERN-OHL-S-2.0-or-later, the manual's pages through the one fact in
  `docs/conf.py`, and the viewer as a separate AGPL-3.0-or-later package

#### Scenario: A page spells a licence literally

- **WHEN** a page under `docs/` other than a historical release note
  spells a licence identifier other than the viewer's, or the README
  spells one other than the viewer's and the framework's current words
- **THEN** the documentation tests fail naming the page

#### Scenario: A 0.7 user upgrades

- **WHEN** a 0.7 user opens the upgrading page
- **THEN** its 0.7 to 0.8 part lists every breaking change of 0.8, the
  install's extras, the import paths, the engines' names, the OpenSCAD
  family, a node's shape, the leaf contract, the symbolic value and the
  removed modules among them, each with what to change

#### Scenario: A reader follows the release note

- **WHEN** a reader opens the changelog
- **THEN** its table of contents reaches the 0.8 release note, which is
  dated 5 October 2026 and sends the reader to the upgrading page
