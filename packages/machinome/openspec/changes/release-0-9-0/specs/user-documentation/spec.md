## ADDED Requirements

### Requirement: The 0.9.0 release is recorded

The release facts of Machinome 0.9.0 SHALL agree wherever they are stated:
`current_version` of the root's `.bumpversion.cfg` states 0.9.0, and every
manifest of the set, every pin between two of its distributions, every file
that restates the version and every npm lock entry of a member state it,
`machinome-mechanics` included. `docs/conf.py` SHALL state `release =
'0.9.0'`, `version = '0.9'`, the release date the pilot names as
`release_date`, the matching viewer 0.9.0, viewer API 29 and document
versions 1 to 13. The changelog's first release section SHALL be
`Machinome 0.9.0`, dated `Released on <dd/Mon/YYYY>`, with no `Unreleased`
section above it, opening with what a maker gets and sending a reader to
the upgrading page for the moves a project may have to follow, its bullets
those written as each change landed. `HISTORY.rst`'s top release entry
SHALL be `Machinome 0.9.0 (<YYYY-MM-DD>)`, opening with what 0.9 is, one
repository of released packages under one licence, one version, one
command, one manual and one release, and keeping every bullet of the road
in the order the road ran them. `docs/releases/release-0.9.rst` SHALL be
the release note of the 0.9 line, its title naming Machinome 0.9 and dated
the release's day, reached from the changelog. The status page SHALL state
the release through its substitutions and that every package of the set is
numbered and released with the framework. `context7.json` SHALL state
0.9.0, its date and the matching viewer 0.9.0, API 29. The changelogs of
the browser viewer, the mechanics helpers, the films and the studio SHALL
each have `0.9.0 — <d Month YYYY>` as their newest release section, the
release's day, with no `Unreleased` section above it; for the films and the
studio it is their first numbered release. The upgrading page SHALL open
with a part for upgrading from 0.8 to 0.9 that names every move a 0.8
project makes, each with what to change: the node types' extras, the former
addresses `machinome_mechanics` and `machinome_viewer`, the version of
`machinome-mechanics`, the viewer flag, the former commands
`machinome-viewer` and `machinome-studio`, the entry point
`machinome.viewer`, the studio's package `floor` and the films' command.

#### Scenario: A reader checks which version the manual describes

- **WHEN** a reader compares the installed package's version with the
  manual's status page, changelog and history
- **THEN** all state 0.9.0, released on the day the pilot named, and the
  changelog's first release section is the 0.9.0 section

#### Scenario: A version copy or a product's changelog is left behind

- **WHEN** the set is bumped to 0.9.0 and the day is placed in the
  framework's records but a product's changelog still opens with
  `Unreleased`, or a copy of the version still states 0.8.1
- **THEN** the release-records test fails naming the product or the copy

#### Scenario: A 0.8 user upgrades

- **WHEN** a 0.8.1 user opens the upgrading page
- **THEN** its first part names each move of 0.9 with what to change, and
  the documentation test fails naming a move the part does not spell

#### Scenario: Work lands after the release

- **WHEN** a change landed after 0.9.0 writes its entry in `HISTORY.rst`
- **THEN** the entry sits in one `Unreleased` section above
  `Machinome 0.9.0 (<YYYY-MM-DD>)`, the release's entry is unchanged, and a
  second `Unreleased` section, or the word anywhere else above the
  release's entry, fails the release-records test

## MODIFIED Requirements

### Requirement: The 0.8.1 release is recorded

The release facts of Machinome 0.8.1 SHALL agree wherever they are
stated, by the same rules as 0.8.0's: the five version files hold the
version `pyproject.toml` states, and `docs/conf.py`'s release block states
the release date, 10 October 2026, the matching viewer 0.8.1, viewer API
29 and document versions 1 to 13. The `viewer` and `web-snapshot` extras
SHALL require the compatible release of `machinome-viewer` 0.8.1,
`~=0.8.1`, since the viewer joined the set (change `join-viewer`), until a
later release moves the pins. The changelog SHALL keep a
release section `Machinome 0.8.1`, dated `Released on
10/Oct/2026`, below any later release's, opening with what a maker gets
and sending a reader to the upgrading page for the changes a project may
have to follow. `HISTORY.rst` SHALL keep the entry
`Machinome 0.8.1 (2026-10-10)` below any later release's.
`docs/releases/release-0.8.rst` SHALL end
with a section naming 0.8.1 and dated 10 October 2026. `context7.json`
SHALL name 0.8.1 and its date among the releases it lists. The
upgrading page SHALL keep a part for upgrading from 0.8.0 to 0.8.1,
below any later part and above the 0.7 to 0.8 part, which stays intact.

#### Scenario: A reader checks which version the manual describes

- **WHEN** a reader reads the changelog and the history after a later
  release
- **THEN** the 0.8.1 section and history entry still state 0.8.1, released
  on 10 October 2026, below the later release's

#### Scenario: A 0.8.0 user upgrades

- **WHEN** a 0.8.0 user opens the upgrading page
- **THEN** its part for 0.8.0 to 0.8.1 names each change since 0.8.0 a
  project may have to follow, with what to change

### Requirement: The 0.8.0 release is recorded

The release facts of Machinome 0.8.0 SHALL agree wherever they are
stated. `pyproject.toml`, `machinome/__init__.py`,
`machinome/vet/universe.toml`, `setup.cfg`'s bumpversion table and
`docs/conf.py`'s `release` SHALL all state the released version, and the
tests SHALL hold them to the version `pyproject.toml` states rather than
to a literal. `docs/conf.py`'s release block SHALL be the one place the
manual states the release date, the matching viewer's version and API,
the document versions and the framework's
licence; a page SHALL state each through its substitution
(`|release_date|`, `|viewer_version|`, `|viewer_api|`,
`|document_versions|`, `|framework_licence|`),
never as a literal.

The framework's licence SHALL be stated as GPL-2.0-or-later or
CERN-OHL-S-2.0-or-later, at the recipient's choice, as the current fact
and nothing more: no comparison with any other licence, no position on
derivative works, no exception and no reason. The framework's licence
SHALL reach a page only through the one fact in `docs/conf.py`,
`|framework_licence|`, and `README.rst` SHALL state the same words. No
`.rst` page under `docs/` other than the historical release notes under
`docs/releases/` SHALL spell a licence identifier literally;
`README.rst` SHALL spell no licence identifier but the exact words of
`docs/conf.py`'s `framework_licence`. The browser viewer SHALL be stated as
a package of the repository under the same licence (change `join-viewer`).

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
  `docs/conf.py`, and the viewer as a package of the repository under it

#### Scenario: A page spells a licence literally

- **WHEN** a page under `docs/` other than a historical release note
  spells a licence identifier, or the README spells one other than the
  framework's current words
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

### Requirement: The mechanics helpers are documented in the manual

The framework manual SHALL document the mechanics helpers, the package
`machinome.mechanics` of the distribution machinome-mechanics, installed by the
`mechanics` extra: a reference section, `reference/mechanics/`, listed in the
reference part of the navigation, whose index names the distribution, its
version, the framework's, through the `|release|` substitution, its install
line and its import, and lists every helper, followed by a conventions page and one
page per formula family stating each helper's signature, frame, zero, sign and
domain with an example; and a how-to guide, `howto/mechanism-formulas`, listed
in the how-to part of the navigation, that installs the helpers, calculates a
pose and connects a helper to a driver through a relation law, explaining
resolved parameters, deferred symbolic inputs and the limit on dimensional
class-body formulas. The installation guide, the helper API reference, the
motion-law guidance and the sibling-manuals page SHALL link those pages
inside the manual. No page SHALL link a separate mechanics manual, and none
SHALL spell the module `machinome_mechanics` but the changelog and the
upgrading page, which record the rename and the 0.7 migration. Every example
of those pages that can run SHALL be run by the mechanics package's tests
against the installed framework, while the manual's own build SHALL import no
runtime package.

#### Scenario: Find a helper from the framework

- **WHEN** a framework user looks for a gear, screw, crank, delta or linkage helper
- **THEN** the manual's reference section lists "Mechanics helpers", whose
  pages give each helper's signature and conventions
- **AND** states that helpers are imported from `machinome.mechanics`

#### Scenario: Follow a motion-law or migration guide

- **WHEN** a reader wants to reuse a mechanical formula or migrate the former
  framework helper imports
- **THEN** they can follow a link inside the manual to the mechanics pages for
  examples and conventions without needing internal workflow records

#### Scenario: The helpers' examples run

- **WHEN** the mechanics package's tests run on a synced workspace
- **THEN** every `>>>` example of the mechanics reference pages and of the
  how-to guide runs against the installed helpers and framework with the
  examples' project on the path, and none fails

#### Scenario: No page sends a reader to the separate manual

- **WHEN** the manual's pages and the framework's README are read
- **THEN** none links `machinome-mechanics.readthedocs.io`, and only the
  changelog, which records the rename, and the upgrading page's 0.7 section
  spell `machinome_mechanics`

### Requirement: The studio is documented in the manual

The manual SHALL document the studio by reader intent: three how-to guides,
"Open a project in the studio" (what it needs, `pip install
"machinome[studio]"`, `playwright install chromium`, `machinome studio
--projects-dir PATH`, the configuration file, then opening or creating a
project from the hub), "Work in a project's workspace" and "Choose and steer
the studio's agents" (the profiles, the per-agent runtimes, the separate Codex
login); and a reference section, "Studio", holding what the studio is and
runs against with its limits, the studio command (its options, the
configuration file, the order in which option, environment, file and default
apply, the module forms, the exit statuses), the project configuration, the
profiles and troubleshooting. The CLI reference SHALL hold a section
`machinome studio` and SHALL NOT say the studio is yet to add its command.
The installation page SHALL name the `studio` extra with its prerequisites
(the OpenSpec CLI, a logged-in agent backend, Chromium as a second step) and
the distribution `machinome-studio` among the packages of the set under the
set's licence. The status page SHALL state the studio's experimental standing
and, from the release that includes it, nothing of an index that does not
serve it.
Every page SHALL spell the command `machinome studio` and the module forms at
`machinome.studio`; none SHALL show `machinome-studio` as a command, `python -m
floor`, `scripts/setup`, a clone of the studio's former repository or a
project of the catalogue as the way to run the studio. The studio's facts the
pages state (the viewer API it requires, the Claude and Codex models and
efforts, the qualified Codex version, the build volume) SHALL be release facts
of the manual's configuration, held to the studio's source by a test, and the
manual SHALL build with warnings as errors from its own requirements file.

#### Scenario: A reader opens the studio from the manual

- **WHEN** a reader follows "Open a project in the studio"
- **THEN** they install with `pip install "machinome[studio]"` and `playwright
  install chromium`, start the hub with `machinome studio --projects-dir
  PATH`, and open or create a project in the browser, without cloning a
  repository or running a setup script

#### Scenario: The former launcher is gone from the pages

- **WHEN** the manual's pages are searched for `machinome-studio
  --projects-dir`, `python -m floor` or the studio's former repository
- **THEN** none is found outside the changelog's line that names the former
  command, and the documentation test fails naming a page that holds one

#### Scenario: A stated fact drifts from the studio's source

- **WHEN** the studio's required viewer API, a qualified model, an effort,
  the qualified Codex version or the build volume changes in its source and
  the manual's release facts do not
- **THEN** the studio's documentation test fails naming the fact
