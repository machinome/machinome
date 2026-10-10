## Context

The release state of 0.7.1 (`openspec/changes/archive/2026-09-27-release-0-7-1/`)
set the shape this change follows: one release block in `docs/conf.py`,
the changelog's `Unreleased` section turned into the version's section and
rewritten as a story, a `HISTORY.rst` entry, the status page, the release
note, `context7.json`, and tests that read the version once from
`pyproject.toml`. `skills/write-the-manual/SKILL.md` ("Release facts are
stated once", "Work after a release", "A release pass") is the procedure.

What differs from 0.7.1:

- **0.8 removes and renames.** 0.7.1 was additive; 0.8 is the lean core's
  first layer, and most of its fifteen changelog bullets carry *Breaking*
  paragraphs (install, framework API, command line, generated source,
  persisted state once). The upgrading page already maps three of the
  families in sections marked *(unreleased)*; it has no 0.7 to 0.8 part
  and no complete list.
- **The bullets were written as each cycle landed**, ten cycles in three
  days, and several describe an intermediate state a later cycle replaced:
  the SCAD presentation bullet names `machinome.openscad` and
  `machinome.scad_engine` (removed by `openscad-out`), the B-rep bullet
  names `require_brep_engine` as the seam (the `brep-mesh` rename) and the
  symbolic-values bullet sends `require_openscad` to
  `machinome.openscad.binary` (now `machinome.node.openscad.binary`). Two
  bullets name a project or the workspace.
- **The licence changes**, and the instruments that grant it (`LICENSE`,
  `NOTICE`, the SPDX headers, `pyproject.toml`'s metadata) are another
  agent's, in a commit the pilot injects separately.
- **The viewer's number is not settled.** The viewer's main carries API 29
  (on-demand capture of a clocked machine) above 0.7.1; the pilot has not
  chosen between releasing it as 0.8.0 and keeping 0.7.1.

## Goals / Non-Goals

**Goals:**
- Every reader-facing record states 0.8.0, released 5 October 2026, and
  the framework's licence as GPL-2.0-or-later or CERN-OHL-S-2.0-or-later.
- A 0.7 user finds, on one page, every breaking change of 0.8 and what to
  change for each, checked against the code.
- The changelog tells a maker what 0.8 gives, in families, describing the
  code at 0.8.0, with no project named.
- The tests refuse the state being fixed: a version file left behind, an
  `Unreleased` section, a licence identifier other than the viewer's
  spelled on a page, a README licence line disagreeing with `conf.py`.

**Non-Goals:**
- No source change, no document version, no behaviour change.
- The licence instruments (`LICENSE`, `NOTICE`, `pyproject.toml`'s
  `license` and classifiers, the SPDX headers, `framework-identity`,
  `AI-USE.md`, `CREDITS.md`, the 0.7.x and older history sections).
- The viewer's release, the studio's and workspace's skills,
  machinome-mechanics, machinome-freecad.
- Building distributions, tagging, pushing, uploading, Read the Docs,
  Context7.

## Decisions

1. **A minor number, 0.8.0** (the pilot's). Names are removed with no
   alias and a bare install changes what it carries; the roadmap reserved
   0.8 for this line. Version files are moved by hand, `bumpversion` not
   run, because its `commit = True` and `tag = True` would commit and tag
   from inside the cycle.

2. **A release-note page, `releases/release-0.8.rst`**, where 0.7.1 was a
   section of `release-0.7.rst`. 0.8 is a new line with its own story
   (install only what you use, one path per name, the engines, OpenSCAD as
   one family, what is kept between runs, the licence, upgrading). It is
   listed in the changelog's toctree above `release-0.7`, and
   `test_the_release_note_has_the_dated_section` derives the page from the
   released version's major.minor: for a `.0` release the page's title
   names the major.minor and the page states the date; for a patch the
   page's last section names the version, as 0.7.1's does. The structure
   test's list of retired pages is unchanged and still refused.

3. **The licence is one release fact.** `framework_licence` joins the
   release block and `rst_prolog`, so a page states it as
   `|framework_licence|`; `ReleaseFactsTest.test_facts_are_substitutions`
   gains the name. `README.rst` is not built by Sphinx and states the words
   literally; a test reads `conf.py`'s value and requires it in the README.
   The licence is stated as the current fact and nothing more: no
   comparison with any other licence, no position on derivative works, no
   exception, no reason. The pin names no licence but the two it admits,
   in the tests' code as on the pages: every `.rst`
   page under `docs/` outside `docs/releases/` spells no licence
   identifier literally (a token of the shape
   `[A-Z][A-Za-z]*(-[A-Z]+)*-\d+\.\d+(-or-later|-only|\+)?`) except the
   viewer's `AGPL-3.0-or-later`, so the framework's licence reaches a page
   only through `|framework_licence|`; `README.rst` spells no identifier
   but `AGPL-3.0-or-later` and the exact words of `conf.py`'s
   `framework_licence`. The changelog is a page like the others; its 0.4
   packaging line now reads "Relicensed the project, with updated
   attribution and NOTICE.". The sibling manuals page and
   `docs/architecture.md` describe `machinome-mechanics` without its
   licence; its own manual states it. Alternative rejected for the framework's own
   licence: a literal on each page pinned by a test, which would make the
   licence commit's author edit five pages.

4. **The viewer's number and API live in two places.** `conf.py`'s
   `viewer_version`/`viewer_api` (read by every page through substitutions)
   and `context7.json`'s rule. The changelog's 0.8.0 section, the release
   note and `HISTORY.rst` state only what is true either way: the document
   versions do not move, so a 0.7 viewer reads a 0.8 export. The
   release-records test holds `context7.json`'s "The matching viewer is
   <viewer_version>, API <viewer_api>" to `conf.py`, so the two cannot
   drift. `test_profile_documentation` pins `viewer_api = '27'`, the API
   that brought profile contact's pairing; it is relaxed to "at least 27",
   which is what the 0.7.0 record it guards needs.

5. **The changelog section is rewritten from the code, not from the
   bullets.** Families in the order a maker meets them: the licence;
   install and the extras; one import path; the two engines and the test
   run's flags; the OpenSCAD family optional; the leaf contract and
   building (production profiles, artifacts); verdicts kept between runs;
   exports and simulation (the revision record, a clocked machine's
   identity); the corrections. Every address, flag, extra and message is
   checked on the bench before it is written; each bullet keeps its
   *Breaking* paragraphs in place, corrected to the final addresses; ADR
   numbers stay; "Born of" lines describe the machine by kind and name no
   project, sibling checkout or workspace path. A "Breaking changes"
   paragraph in the opening lists each breaking change in one line and
   sends the reader to :doc:`upgrading`.

6. **The upgrading page gains a part, and the three sections move under
   it.** "Upgrading from Machinome 0.7 to 0.8" is a top-level title above
   the 0.6 to 0.7 title, so the page has two parts; its opening is the
   complete list, each item with what to change and a link to its section
   below where one exists. The three existing sections lose *(unreleased)*
   and "the next release" wording; the one sentence in the 0.6 to 0.7 part
   that says the engine variable is renamed "in the next release" names
   0.8. Items without a section (the removed modules, `shape()`'s type,
   the symbolic value, the leaf hooks, the `.scad` files no longer kept)
   are stated in the list itself.

7. **The 0.7.1 requirement is corrected, not left contradicting the new
   one.** "The 0.7.1 release is recorded" requires 0.7.1 to be the top
   entry, the status page's version and `context7.json`'s; after this
   change none is. Its version-file agreement moves to the 0.8.0
   requirement (stated for "the released version"); what stays is that the
   0.7.1 section, history entry and release-note section remain, dated,
   below the later release. The same reasoning as 0.7.1's decision 6.

8. **The status page states direction as fact.** "Production information"
   leaves the Direction section because production profiles ship in 0.8;
   what is stated is that the package split has not started and nothing is
   published as a separate package. The caveat phrases stay refused
   everywhere but the status page and `releases/`.

9. **The OpenSCAD snapshot needs its extra.** Since `openscad-out` the
   default renderer of `machinome snapshot` is the `openscad` row of the
   table of supported node types, refused without `machinome[openscad]`
   naming it and `--renderer web`, and it runs the OpenSCAD executable. The
   viewer-provenance requirement, `install.rst` and the README say a
   framework installation without the viewer snapshots through OpenSCAD
   with the `openscad` extra.

10. **The campaign plan records the merge.** `workflow/ongoing/lean-core.md`'s
   last section gains one paragraph: the line was merged into framework
   `main` as 3435b35 on 5 October 2026 (a merge: `main` had taken three
   workflow-only commits since the fork), and the release state is this
   change. Nothing else in the plan changes.

11. **A handoff record, `workflow/ongoing/release-0.8.0.md`**, for the pilot
   and the licence agent: the licence instruments listed by file and count
   only, counts taken by grep on the bench, never naming the licence they
   carry; that a commit injected before the 0.8
   cycles reaches none of the files those cycles created, which need their
   headers at the tip; the pilot's steps; the follow-ups outside the
   framework; why no distribution is built.

## Risks / Trade-offs

- [The disagreement between the pages and the instruments at this
  commit is read as an error] → the proposal, the handoff and the evidence
  say that the division of labour exists; the pages carry the licence 0.8
  ships under, the instruments follow in the pilot's commit.
- [The pilot keeps the viewer at 0.7.1] → `conf.py` and `context7.json`
  change, and `test_the_matching_viewer_is_numbered_with_the_framework` is
  retired with them; no page or record states the number otherwise.
- [A bullet is described from its proposal rather than the code] → each
  address, flag and message is probed on the bench (import, grep) before
  it is written; the evidence records the probes.
- [The upload slips past 5 October] → the date lives in `conf.py`
  (`release_date`), the changelog head, `HISTORY.rst`, the release note and
  `context7.json`; the handoff names them.
- [A test elsewhere reads the `Unreleased` section or the 0.7.1 literal] →
  `grep -rln -i unreleased tests` names three files; each is checked, and
  the full suite is run by the orchestrator before commit 2.
