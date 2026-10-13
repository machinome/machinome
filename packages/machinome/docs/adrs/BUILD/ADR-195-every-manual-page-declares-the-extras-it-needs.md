# ADR-195: Every Manual Page Declares the Extras It Needs

**Status:** Accepted
**Date:** 2026-10-12
**Change:** [`manual-extras`](../../../openspec/changes/archive/2026-10-13-manual-extras/)
**Related to:**
- [ADR-182: The repository is a monorepo of distributions, each named by its directory](ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md): the manual stays inside the framework's package, `packages/machinome/docs/`, and is the whole set's
- [ADR-188: The browser viewer is a product of the repository, numbered with the set](ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md): the first product whose manual folded into the framework's, by reader intent
- [ADR-020: Static export and embeddable viewer widget](../EXPORT/ADR-020-static-export-and-embeddable-viewer-widget.md): the framework's own Sphinx directive, `machinome.sphinx`, a project's manual uses too; this decision does not touch it

## Context and Problem Statement

Since the joins, the framework's one manual holds the pages of every product
of the set: the browser viewer, the mechanics helpers, the skills, the films
and the studio fold into it beside the framework's own pages. A reader of the
bare framework, `pip install machinome`, cannot follow many of them without
an extra, and nothing told that reader so before they read. On the line
`v0.9-joins` at 462f7119 the manual had 77 pages outside the release notes;
read against what each page's commands and code need, 50 needed at least one
extra and 27 none, and of the 50, 8 named their extra before their first
section heading, 8 further down and 34 nowhere. The installation page listed
the extras in a table and paragraphs kept by hand, and named no extra for the
studio.

Reading the pages for their needs found two claims false: the installation
page installed the tutorial with `machinome[viewer,cadquery]`, but chapters 4
to 10 need build123d, which reduces the `Svg` artwork of the counter's
digits (chapter 4's model is refused naming `machinome.node.build123d`
without it); and chapter 1 says the tutorial needs no OpenSCAD, but chapter
10's first two `machinome snapshot` lines take the default OpenSCAD viewer.

The pilot decided on 12 October 2026 (`workflow/ongoing/release-0.9.md` at
the repository root, decision 9) that the manual stays inside the
framework's package, that the other products' pages fold into it, and that
one cycle gives every page the extra it needs, rendered at the top of the
page by the manual's own extension, pinned by a test, the installation
page's list derived from the same declarations.

## Considered Options

1. **A directive, `.. needs::`, the first thing under each page's title**,
   read and rendered by the manual's own Sphinx extension (chosen)
2. A docinfo field, `:needs:`, above the title: Sphinx reads it as the
   page's metadata only before the title, and the same field written after
   the title silently renders as a field list instead of failing
3. Prose on each page, kept by hand: the state that was the finding, with
   nothing to derive the installation page's list from and nothing to test

## Decision Outcome

**The declaration.** Every page of the manual but the release notes under
`docs/releases/` (`manual_extras_exempt` in `conf.py`) begins, as the first
element under its title, with `.. needs::` and the extras a reader installs,
beyond `pip install machinome`, to follow the page as written, or `none`.
For extras it renders one line at the top of the page, `Needs pip install
"machinome[<extras>]"` in the table's order, and what those extras need
outside pip, each such need once, "Needs" linking to the installation page's
list; for `none` it renders nothing.

**The extension and its table.** `docs/_ext/manual_extras.py` is the
manual's own extension, listed in `conf.py`, not a module of the framework's
package; it imports Sphinx, docutils, `packaging` and the standard library,
so the manual still builds from `docs/requirements.txt` alone. What each
extra is for and what it needs outside pip is its table,
`docs/_ext/manual_extras.toml`, one row per extra a reader installs, in the
order the installation page lists them; the distributions each installs are
read from the framework's manifest.

**The installation page derives its list.** `.. extras::` under the label
`extras` renders every extra of the manifest but `dev` and `docs`: its
install name, the distributions its requirements name (with their extras),
or each member for an extra that names other extras of the framework, what
it is for, what it needs outside pip, and the pages that declare it, the
tutorial once and a reference section once by its index. It replaces the
hand-kept table and paragraphs. The page's tutorial line names the extras
the tutorial's chapters declare, `viewer,cadquery,build123d`.

**What fails.** The build fails, under warnings as errors (`make docs`, CI,
Read the Docs), on a page that declares nothing, a declaration naming an
extra the table lacks, an extra twice or `none` with another, a declaration
that is not the first thing under the title or is the page's second, and a
table whose extras are not the manifest's. The documentation structure test
fails on the same before any build, and holds the declarations to rules: a
product's reference section declares its product's extra alone; the core's
rules and records declare `none`; a tutorial chapter, a how-to guide but the
one that chooses among the node types, and the first machine's page declare
at least what their code needs, read from their code blocks and the modules
they include.

### Consequences

- Good: a reader who lands on any page sees, before its first paragraph,
  the one `pip install` line and the outside-pip steps the page needs, or
  nothing when the bare framework suffices.
- Good: an extra is described once, in the table, and the installation
  page's list follows the manifest; a new extra fails the build until the
  table has its row.
- Good: a new page declares or the build says so, and a teaching page's
  declaration is held to its code.
- Bad: a declaration made by judgment (the viewer on a page whose steps are
  watched in it) is held by review alone, not by a derived rule.
- Neutral: a page's own install section stays where it says more than the
  line (the movie's setup output, FreeCAD's checksum).
- Neutral: the framework's source archive carries every file the
  manual's build reads, which a test holds, and building the pages needs
  the set's other packages installed beside them, from the index once
  0.9.0 is uploaded or from the repository.

## References

- `packages/machinome/docs/_ext/manual_extras.py`,
  `packages/machinome/docs/_ext/manual_extras.toml`,
  `packages/machinome/docs/_static/manual-extras.css`,
  `packages/machinome/docs/conf.py`,
  `packages/machinome/docs/start/install.rst`
- `tests/test_docs_structure.py` (`PageExtrasTest`),
  `tests/test_manual_extras.py`, `tests/test_repository_layout.py`
- `openspec/specs/user-documentation/spec.md`,
  `openspec/specs/framework-contributor-guidance/spec.md`
