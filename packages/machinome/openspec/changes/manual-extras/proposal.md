## Why

Since the joins, the framework's one manual holds pages a reader of the bare
framework cannot follow without an extra, and nothing tells that reader so
before they read. On the line `v0.9-joins` at 462f7119 the manual has 77
pages outside the release notes under `releases/`. Read against what each
page's commands and code need (design.md, "The declarations"), 50 of them
need at least one extra beyond `pip install machinome` and 27 need none.
Of the 50, 8 name their extra before their first section heading, 8 name it
further down, in their own words, and 34 name no extra at all: the ten
mechanics reference pages under the section's index, seven of the nine
viewer reference pages, the
movie document's page, nine of the ten tutorial chapters, and seven how-to
guides (STEP and STL, sheet, springs, markings, sharing an export,
embedding the viewer, a movie's stage). The installation page lists the
extras in prose and a table kept by hand: a twelve-row table for the node
types and engines, a paragraph for `mechanics`, `skills`, `movie` and
`web-snapshot`, a sentence for `viewer`, nothing for `studio`.

Reading the pages for their needs found two claims that are false today,
both proved by building the tutorial's own project with the other node
packages hidden (design.md, probes 2 and 3):

- the installation page installs the tutorial with
  `pip install "machinome[viewer,cadquery]"`, but chapters 4 to 10 need
  `build123d` too: the counter's digits are `Svg` artwork, which the
  `build123d` node package reduces. Chapter 4's model is refused,
  `No module named 'machinome.node.build123d'`, where chapters 1 to 3 and
  the first machine build;
- chapter 1 says the tutorial "stays with CadQuery so that nothing here
  needs OpenSCAD", but chapter 10's first two `machinome snapshot` lines use
  the default OpenSCAD renderer, refused without the `openscad` extra.

The pilot decided on 12 October 2026 (`workflow/ongoing/release-0.9.md` at
the repository root, decision 9) that the manual stays inside the
framework's package, that the other products' pages fold into it, and that
"one small cycle gives every page the extra it needs, rendered at the top of
the page by the manual's own extension, pinned by a test, the installation
page's list derived from the same declarations". This is that cycle, the
seventh of that note's road.

## What Changes

- **A declaration on every page.** Each page of the manual but the release
  notes begins, under its title, with `.. needs::` naming the extras a
  reader installs to follow it, or `none` (design.md, Decision 1). The 77
  pages of the base and the eight pages `join-studio` adds declare as
  design.md's table of declarations states.
- **The manual's own Sphinx extension**, `docs/_ext/manual_extras.py`, with
  its table of extras `docs/_ext/manual_extras.toml` (what each extra is
  for and what it needs outside pip), listed in `conf.py`'s `extensions`
  (Decisions 2 and 3). The directive renders, at the top of a page that
  needs something, one line: `Needs pip install "machinome[...]"` and what
  those extras need outside pip; it renders nothing for `none`. The build
  fails on a page without a declaration, an extra the table lacks, a
  declaration that is not the first thing under the title, and a table that
  is not the manifest's set of extras.
- **The installation page derives its list.** A second directive,
  `.. extras::`, renders every extra the framework's manifest declares, in
  the table's order, with the distribution the manifest names, what it is
  for, what it needs outside pip, and the pages that declare it. It
  replaces the hand-kept twelve-row table and the paragraph on the four
  other extras; the page's install line for the tutorial names
  `viewer,cadquery,build123d`, the extras the tutorial's chapters declare
  (Decision 4).
- **The pins, red first** (Decision 5): `tests/test_docs_structure.py`
  holds every page to one declaration in its place, naming extras of the
  table; the table to the manifest; a product's reference section to its
  product's extra; the core's reference, concept and project pages to
  `none`; a tutorial or how-to page to every extra its code imports or runs;
  the installation page to the directive and to the tutorial's extras.
  `tests/test_manual_extras.py` builds small Sphinx projects with the
  extension and holds what it renders and what it refuses. The two
  installation-page tests that read its source for extras and
  distributions read the rendered list instead.
- **The rule for a page's author** is stated where one writes a page: the
  manual's `project/contributing.rst` and the contributor guide's pull
  request steps (Decision 6).
- **Records**: `HISTORY.rst` and the manual's changelog gain their
  `Unreleased` bullets; `docs/architecture.md` gains a row for the manual;
  ADR-195, "Every manual page declares the extras it needs", is new
  (Decision 7).

Not in this change: the text of chapter 10's photograph section, which
contradicts chapter 1 (its declaration says what it needs as written; the
contradiction goes to `workflow/warts.md` for the pilot, Open Questions 6);
`MANIFEST.in`, whose `docs` line already leaves the manual unbuildable from
the source archive (Open Questions 7); the workspace's `write-the-manual`
skill (the campaign's `workspace-consistency` cycle); any version bump, push
or upload.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: every page declares the extras it needs and shows
  them at its top; the installation page derives its list of extras from
  the manifest and the declarations; the tutorial's install line names the
  extras its chapters declare.
- `framework-contributor-guidance`: the contributor guide states that a
  manual page begins with its declaration.

`kernel-extras` is unchanged: its requirement that the installation page
name, for each extra installing a distribution of the set, the distribution
it installs holds of the rendered list, which a test reads (design.md,
Decision 8).

## Impact

- **Manual.** Two new files under `docs/_ext/`, one under `docs/_static/`;
  `conf.py` (one `sys.path` line, the extension, two settings); one line
  inserted under the title of each of the 77 pages; the installation page's
  extras section rewritten; one clause each in `start/first-machine.rst`
  and the installation page's requirements; one sentence in
  `project/contributing.rst`. `docs/requirements.txt` and
  `.readthedocs.yaml` are unchanged: the extension imports Sphinx, docutils,
  `packaging` (a requirement of Sphinx) and the standard library.
- **Tests.** `test_docs_structure.py` (a new class, two tests rewritten),
  the new `test_manual_extras.py`, one test added to
  `test_repository_layout.py`.
- **Records.** Two delta specs; ADR-195 and its index line; `HISTORY.rst`;
  the manual's changelog; `docs/architecture.md`; `CONTRIBUTING.rst`.
- **Other cycles.** Written on 462f7119, before `release-tooling`,
  `join-studio` and `viewer-seam` land; the orchestrator fast-forwards the
  bench before this planning commit. Where the text assumes them is listed
  in design.md, "Assumptions about the cycles before this one".

Originating evidence: the pilot's decision 9 of 12 October 2026, the count
of design.md's table of declarations, and probes 1 to 7 of design.md.
