## MODIFIED Requirements

### Requirement: The README describes the package

`README.rst`, the landing page of the framework's directory
`packages/machinome/` and the distribution's long description, SHALL present Machinome as it is, to a reader who does not
know it: what the framework is and what belongs in a machine's source; what
that source looks like, as Python the suite builds; what the framework does
with it (incremental builds, tests, simulation, the browser viewer and
static exports); how to install it and name the extras its parts need, with
the viewer's separate licence visible before the extra is installed; where
the manual, the tutorial, the changelog and the upgrading page are; the
framework's licence in the exact words of `docs/conf.py`'s
`framework_licence`; and where contributors go.

The README's sections SHALL be exactly these, in this order: *Machinome*
(the title), *A machine's source*, *What the framework does*, *Install*,
*Documentation*, *Licence*, *Contributing*. The README SHALL be at most
1500 words, so that an addition is a trade for something already there.

The README SHALL NOT carry a release narrative: no heading SHALL name a
version, and no sentence SHALL state a version of Machinome or of its
former name. The current version, its date, what a release changed and the
lineage of the name SHALL stay in the changelog, the release notes, the
status page, the upgrading page and `HISTORY.rst`, which the README links.

The README SHALL contain at least one Python code block, and every Python
code block in it SHALL be the verbatim text, or a verbatim contiguous part,
of a module under `docs/tutorial/counter/` that the suite builds: a
chapter's module, or a module of the tutorial project declared as a model
for the README. The example SHALL place every moving part by a frame on a
frame, a mate stated in the assembly, and SHALL NOT place a part in
`render()`: no Python block of the README SHALL contain `translate(`, and
one SHALL state a mate with `.on(`.

The README shows and the manual teaches. The prose around the example
SHALL name each declaration of the block in one clause, in the same voice
for every one of them, SHALL define no term and SHALL state no mechanism;
the manual page that explains a thing is linked, not restated. A change to
the README SHALL edit the fact it changes, in place; it SHALL add no
section and no paragraph, and the README SHALL carry no account of a change
made to it, of why its text is as it is, or of the reasoning of whoever
changed it.

The repository's own landing page is the root `README.md`: it SHALL show
what the repository holds, one line for each package under `packages/`
linking its directory, and the licence every package carries, and SHALL
carry no version, no release narrative and no account of a change.

Guidance for contributors — the development environment, how to run the
tests and the spec-first discipline — SHALL live in `CONTRIBUTING.rst`,
which the README links; the README SHALL NOT restate it, and the layout of
the package SHALL stay in the contributor briefing.

#### Scenario: A reader lands on the README

- **WHEN** a reader who has never heard of Machinome opens the README on
  PyPI or in the framework's directory on GitHub
- **THEN** they read what Machinome is, see a machine's source as code the
  suite builds, and find the install line, the manual and the licence,
  without meeting a section named after a version

#### Scenario: A release passes

- **WHEN** a release moves the version, the date and the changelog
- **THEN** the README needs no edit, and a heading or a sentence naming a
  version of Machinome in it fails the documentation tests

#### Scenario: A section is added

- **WHEN** a change adds a section to the README, renames one or reorders
  them
- **THEN** the documentation tests fail naming the headings found

#### Scenario: The README grows

- **WHEN** a change leaves the README longer than 1500 words
- **THEN** the documentation tests fail naming the count

#### Scenario: An agent is asked to change the example

- **WHEN** a change replaces or corrects the README's example
- **THEN** the prose around it names the new declarations at the altitude
  of the others, the page keeps its sections and its size, and nothing in
  it says that the example was changed or why

#### Scenario: The example drifts from the tutorial

- **WHEN** a Python code block in the README is not the verbatim text of a
  tutorial module, or the README has no Python code block
- **THEN** the documentation tests fail naming the block

#### Scenario: The example places a part by hand

- **WHEN** a Python code block in the README places a part with
  `translate(`, or no block states a mate with `.on(`
- **THEN** the documentation tests fail naming the block

#### Scenario: A contributor looks for how to run the suite

- **WHEN** a contributor opens `CONTRIBUTING.rst`
- **THEN** it states the development install, how to run the tests and the
  lint, the browser-snapshot opt-in and the spec-first discipline, and
  points to the contributor briefing for the layout of the package

#### Scenario: A reader opens the repository

- **WHEN** a reader opens the repository's root on GitHub
- **THEN** the root `README.md` names each package under `packages/` with
  one line and a link to its directory, and states the licence, and the
  layout test fails if a package directory is not linked or the licence
  words differ from the manual's `framework_licence`

### Requirement: The documentation build produces nothing

Building the manual SHALL require only what `docs/requirements.txt` lists:
Sphinx, its theme and the published `machinome-viewer` package, which
completes the committed exports with its widget. The Read the Docs
configuration and the CI docs job SHALL both install that file and run
Sphinx, and neither SHALL run `machinome export`, install a system package,
a Node tool or a package from a repository URL, or check out a submodule.
Every export a page embeds SHALL be committed under `docs/_exports/`.

The Read the Docs configuration SHALL sit beside the manual, at
`packages/machinome/.readthedocs.yaml`, and SHALL name the requirements
file and the Sphinx configuration by their paths from the repository
root, `packages/machinome/docs/requirements.txt` and
`packages/machinome/docs/conf.py`, since Read the Docs reads every path in
it from there. The CI docs job, in the repository's workflow at
`.github/workflows/python-app.yml`, SHALL run from the package directory,
where it installs `docs/requirements.txt` and builds `docs`.

Both builds SHALL treat warnings as errors, and the manual's Sphinx
configuration SHALL make every build nitpicky, so that a cross-reference
whose target the manual does not document, written in a page or in a
docstring the manual renders, fails the build that Read the Docs and the
CI docs job run.

#### Scenario: Read the Docs builds the manual

- **WHEN** Read the Docs builds any version of the manual
- **THEN** its configuration names no build job, no apt package and no Node
  tool, installs `packages/machinome/docs/requirements.txt` alone, and the
  build takes the time Sphinx alone takes

#### Scenario: A page embeds an export nobody committed

- **WHEN** a `.. machinome::` directive names a directory outside
  `docs/_exports/`
- **THEN** the suite fails naming the page, before any documentation build

#### Scenario: A build configuration grows a build step

- **WHEN** the Read the Docs configuration or the CI docs job gains an
  export command, a repository install, an apt package, a Node tool or a
  submodule checkout
- **THEN** the suite fails naming the file and the step

#### Scenario: The manual builds from the requirements alone

- **WHEN** a fresh environment installs `docs/requirements.txt` and builds
  the manual with warnings as errors
- **THEN** the build succeeds and every tutorial page shows its committed
  export with the viewer's widget

#### Scenario: A reference names nothing the manual documents

- **WHEN** a page or a rendered docstring cross-references a target the
  manual does not document, such as a class named without its module
  where the current module does not hold it, or a docstring line napoleon
  reads as a type
- **THEN** the CI docs job's command, `python -m sphinx -b html -W docs
  <out>`, fails naming the reference, with no `-n` on its command line,
  and the suite fails if the manual's configuration stops being nitpicky

#### Scenario: The configuration names the manual from the repository root

- **WHEN** the suite reads `packages/machinome/.readthedocs.yaml`
- **THEN** its one install entry is the requirements file
  `packages/machinome/docs/requirements.txt` and its Sphinx configuration
  is `packages/machinome/docs/conf.py`, and the suite fails naming the path
  if either names the manual from the package directory instead

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
have to follow. `HISTORY.rst`'s top release entry SHALL be
`Machinome 0.8.1 (2026-10-10)`; work landed after it SHALL be recorded as
it lands in one `Unreleased` section above that entry, and the word SHALL
appear nowhere else above it. `docs/releases/release-0.8.rst` SHALL end
with a section naming 0.8.1 and dated 10 October 2026. `context7.json`
SHALL state 0.8.1, its date and the matching viewer 0.8.1, API 29. The
upgrading page SHALL open with a part for upgrading from 0.8.0 to 0.8.1,
above the 0.7 to 0.8 part, which stays intact.

#### Scenario: A reader checks which version the manual describes

- **WHEN** a reader compares the installed package's version with the
  manual's status page, changelog and history
- **THEN** all state 0.8.1, released on 10 October 2026, and the
  changelog's first release section is the 0.8.1 section

#### Scenario: Work lands after the release

- **WHEN** a change landed after 0.8.1 writes its entry in `HISTORY.rst`
- **THEN** the entry sits in one `Unreleased` section above
  `Machinome 0.8.1 (2026-10-10)`, the release's entry is unchanged, and a
  second `Unreleased` section, or the word anywhere else above the
  release's entry, fails the release-records test

#### Scenario: A 0.8.0 user upgrades

- **WHEN** a 0.8.0 user opens the upgrading page
- **THEN** its first part names each change since 0.8.0 a project may
  have to follow, with what to change

#### Scenario: A maker installs the viewer extra

- **WHEN** a maker installs `machinome[viewer]` 0.8.1
- **THEN** the requirement names `machinome-viewer>=0.8.1`, the viewer
  the manual declares as matching
