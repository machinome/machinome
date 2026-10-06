## ADDED Requirements

### Requirement: The README describes the package

`README.rst`, the repository's landing page and the distribution's long
description, SHALL present Machinome as it is, to a reader who does not
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

Guidance for contributors — the development environment, how to run the
tests and the spec-first discipline — SHALL live in `CONTRIBUTING.rst`,
which the README links; the README SHALL NOT restate it, and the layout of
the package SHALL stay in the contributor briefing.

#### Scenario: A reader lands on the README

- **WHEN** a reader who has never heard of Machinome opens the README on
  PyPI or GitHub
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
