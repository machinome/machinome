## Why

The 0.9 road is complete on the line `v0.9-joins`: the framework is a
monorepo of eighteen distributions (the core, two engines, nine node types,
the OpenSCAD viewer, and the mechanics helpers, the browser viewer, the
skills, the films and the studio joined from repositories of their own), one
command contributed to by packages, one manual and one release tooling
(`workflow/ongoing/release-0.9.md` at the repository root, "The cycles, in
order", 1 to 9). Every record still says 0.8.1: seventeen manifests and the
manual state the set's version 0.8.1, which was never uploaded, and the
mechanics helpers state their own 0.1.0. On 12 October 2026 the pilot decided
how 0.9.0 is released (`release-0.9.md`, decisions 2 and 10, cycle 10, and
"Held for the pilot"): everything is bumped to 0.9.0 in one bump from the
root's `.bumpversion.cfg`, mechanics and the skills included, which ends the
mechanics helpers' own version (ADR-187); one tag, `v0.9.0`, marks the set;
the number is declared once, as `current_version`; the release sections are
dated by the pilot, who names the day; the upgrading page gets its 0.9
section; `make dist` builds the archives into `dist/v0.9.0`; the tag, the
push, the upload, the Read the Docs dashboard and the fate of the original
repositories are the pilot's.

Probing the day on a copy of the line's head (design.md, probes 1 to 13)
found that the release cannot be one bump of a clean tree as the line stands:
`make bump VERSION=0.9.0` with the mechanics helpers' tables added while their
manifest states 0.1.0 stops in bump2version (`VersionNotFoundException: Did
not find 'version = "0.8.1"' in file:
'packages/machinome-mechanics/pyproject.toml'`), and `make bump` refuses a
tree whose tracked files changed, so the hand step that moves them has to be
a commit of its own before the bump. It also found six tests that pin
0.8.1, the helpers' 0.1.0 or an `Unreleased` heading and fail on the dated
tree (the framework's identity test and its reading of the changelog's
current section, the viewer's, the movie's, the studio's and the mechanics
helpers' changelog tests), and the viewer's `describe` example, which a
seventh holds to the package.

## What Changes

The change has two halves (design.md, Decision 1).

**Before the day**, one commit on the bench, reviewed and committed by the
orchestrator, the suite green at 0.8.1:

- **The mechanics helpers are numbered with the set** (Decision 3): their
  manifest at the set's version, 0.8.1, their requirement
  `machinome~=0.8.1`, the core's `mechanics` extra
  `machinome-mechanics~=0.8.1`, two tables in `.bumpversion.cfg`, `uv.lock`
  relocked; `scripts/check-dist` smokes them at the framework's version;
  `docs/conf.py` loses `mechanics_version` and its substitution, the pages
  that stated it state `|release|` (the 0.7 upgrading part the literal
  0.1.0); `context7.json`'s mechanics rule, the HISTORY's join bullet and
  one new bullet in `HISTORY.rst` and the manual's changelog, the
  mechanics changelog's join bullet; ADR-187 amended; the mechanics
  package's own specs brought current in place.
- **The release-records test without the exception, and the day's
  expectations dormant until the day** (Decision 4): the own-version
  branches gone, the mechanics tables held as the OpenSCAD viewer's are,
  and a new test that each product numbered with a released version of
  the set records that release in its changelog, dated the release's day;
  the tests that pinned 0.8.1 or `Unreleased` read the set's version and
  accept either the `Unreleased` section or the release's.
- **The upgrading page's 0.9 part** (Decision 5): one introduction and
  seven moves above the two subsections the seam and the command wrote,
  pinned by a new test; the installation page's "Upgrading" paragraph sends a
  0.8 user there.
- **The pilot's day note**, `workflow/ongoing/release-0.9.0-day.md` at the
  repository root (Decision 9).

**On the day**, once the pilot names the date, a fresh agent makes one
commit, "Release 0.9.0" (Decisions 2, 6 to 8):

- `make bump VERSION=0.9.0` on the clean bench: every manifest, pin, copy
  and lock to 0.9.0, the mechanics helpers among them.
- The records dated: `docs/conf.py` `version = '0.9'` and `release_date`;
  `HISTORY.rst`'s `Unreleased` becomes `Machinome 0.9.0 (<YYYY-MM-DD>)` with
  its opening; the manual's changelog `Machinome 0.9.0`, `Released on
  <dd/Mon/YYYY>`, with its opening and the moves a project may follow;
  the new release note `docs/releases/release-0.9.rst`; the status page;
  `context7.json`; the changelogs of the viewer, the mechanics helpers, the
  films and the studio, each `0.9.0 — <d Month YYYY>`; the viewer's
  `describe` example; the viewer's own release specs in place. Every text is
  drafted verbatim in design.md, Decision 7, for the applier to place.
- The tests green, `make test` whole, `make docs`, `make check`; the commit;
  the orchestrator's fast-forward of `main`; `make dist` into
  `dist/v0.9.0`; then the archive of this change and the plan's progress
  entry.

**Not in this change**: the tag `v0.9.0`, the push of `main` and the tag,
`make upload`, the Read the Docs dashboard and the retirement of the
mechanics and viewer projects there, the Context7 refresh, the original
repositories on GitHub, and the 0.8.1 archives that were never uploaded. The
day note lists them for the pilot. No source or behaviour changes beyond the
mechanics helpers' version and pins; no document version or viewer API
moves (viewer API 29, document versions 1 to 13).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: a new requirement, "The 0.9.0 release is recorded";
  "The 0.8.1 release is recorded" stops requiring 0.8.1 to be first and
  keeps it as a released record; "The 0.8.0 release is recorded" and "The
  mechanics helpers are documented in the manual" lose the mechanics
  version as a release fact of its own; "The studio is documented in the
  manual" drops the status page's "no index serves it" from the release
  that includes the studio.
- `framework-identity`: the one-version rule without the mechanics
  exception ("The framework is the package directory `packages/machinome`
  of a monorepo"), and the `mechanics` extra pinned `~=` the framework's
  version with the studio's publication clause ended ("Extras select
  independent Machinome products").
- `mechanics-distribution`: the `mechanics` extra pins the distribution
  `~=` the framework's version.

`release-tooling` is unchanged: `make bump`, `make dist` and `make upload`
are used as they are specified.

## Impact

- Before the day: `packages/machinome-mechanics/pyproject.toml`, its
  `CHANGELOG.md`, its two specs and two tests; `packages/machinome/pyproject.toml`
  (one extra); `.bumpversion.cfg` (two tables); `uv.lock`;
  `scripts/check-dist` (the mechanics row); `docs/conf.py`;
  `reference/api.rst`, `reference/mechanics/index.rst`, the status page and
  the installation and upgrading pages; `HISTORY.rst`, the
  manual's changelog, `context7.json`; ADR-187 and its index line; the tests
  `test_release_records.py`, `test_mechanics_boundary.py`,
  `test_docs_structure.py`, `test_machinome_identity.py`,
  `test_viewer_documentation_links.py`, `test_repository_layout.py`'s
  docstring, the viewer's `test_documentation.py`, the movie's
  `test_repository.py`, the studio's `test_documentation.py`;
  `workflow/ongoing/release-0.9.0-day.md`.
- On the day: the twenty-nine files `make bump` moves (design.md, probe 3),
  the records listed above, the new release note, the viewer's `cli.rst`
  example and its own two specs; `dist/v0.9.0` (ignored) in the checkout the
  pilot uploads from.

Standalone release cycle on the bench `v0.9-release` (branch `v0.9-release`,
cut from the line `v0.9-joins` at c5eeb038), its planning commit made on the
line's closed head after `manual-extras`. Authorization: the pilot's
decisions of 12 October 2026 in `release-0.9.md`; the orchestrator's review
is the ratification gate; the orchestrator commits, integrates and stops at
the release day, when the pilot gives the date and the go.
