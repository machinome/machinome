## Context

Viewer `main` is `cb39942`. Since 0.7.1 (`40031a5`) five changes landed
there and are archived: `track-a-part-on-screen`, `highlight-a-part` and
`move-up-and-field-of-view` (29 September, together viewer API 28),
`deterministic-asset-load-order` (29 September, no API or document
change) and `on-demand-clocked` (1 October, API 29). The widget's
`package.json` declares `machinomeViewerApi` 29 and
`machinomeDocumentVersions` 1 to 13; the package, the widget and both
`version` fields of `package-lock.json` say 0.7.1.

The changelog's `Unreleased` section records only `on-demand-clocked`:
the three API 28 changes and the asset-order correction wrote no bullet
when they landed. The 0.8.0 section is therefore written from the
archived changes and checked against the source, not moved verbatim.

The framework's `main` (`ee26e81`, `release-0-8-0`) already states
Machinome 0.8.0, 5 October 2026, viewer 0.8.0, viewer API 29 and
document versions 1 to 13, and says its exports still declare document
versions 1 to 13, as 0.7's do. Mechanics stays 0.1.0 and is not
re-released.

Six places state the framework's licence today: `README.md`,
`docs/index.rst`, `docs/sharing.rst`, `context7.json`, the 0.7.0 section
of `CHANGELOG.md` and the project context of `openspec/config.yaml`. The
first four are exactly the pages `tests/test_licence.py` already holds as
reader-facing for the viewer's grant.

## Goals / Non-Goals

**Goals:**
- Every reader-facing record states 0.8.0, released with Machinome 0.8.0
  on 5 October 2026, API 29, document versions 1 to 13, and the package,
  widget, lock file and bundle banner agree.
- The changelog tells a reader, in families, what 0.8.0 gives a host and a
  maker over 0.7.1, and where each capability arrived (API 28 or 29).
- No current page, record or this change's own artifacts name a licence
  other than the viewer's; a test keeps it so.

**Non-Goals:**
- Any widget, server or capture change; any API or document version move.
- Rewriting records: `workflow/release-0.7.md`, the ADRs and the archived
  changes stay as written.
- Tags, pushes, uploads, Read the Docs, Context7, `scripts/check-dist`.

## Decisions

1. **The release is a version section, not a renumbering.** Unlike
   0.7.1, 0.8.0 carries new behaviour, so its section is written as the
   0.7.0 section is: a reader's story under "What a host gets" and "What
   a maker gets", one line per capability naming its archived change, and
   a short "Compatibility" paragraph (API 28 and 29, documents 1 to 13,
   a 0.7 viewer reads a 0.8 export, this viewer reads every 0.7 export,
   a bundle reporting 27 has none of the API 28 members). Timing and
   test counts from the `Unreleased` bullet do not move into it. No
   project, film or tool name appears, as the documentation test already
   refuses on the manual pages.
2. **The released API is now the substitution.** While the source ran
   ahead of 0.7.1, the home page, the compatibility page and the mount
   reference wrote the released API as a literal 27 beside
   `|viewer-api|` for the source. At 0.8.0 the release and the source
   agree, so those pages state `|viewer-api|` alone and the literal goes;
   the test compares the changelog's `viewer API 29` and the `describe`
   example with `package.json`. "API 27, the 0.7.0 release" stays in the
   compatibility history, which is when that API arrived.
3. **The licence is stated once per page, as the viewer's.** Each of the
   six sentences keeps the viewer's grant and replaces the framework's
   licence with "licensed separately", sending the reader to the
   framework's manual where a page has a link to it. The rewrite of the
   0.7.0 changelog sentence is minimal and changes no other fact of that
   section. `tests/test_licence.py` gains a check over `README.md`,
   `CHANGELOG.md`, `context7.json` and every `docs/**/*.rst`: every
   SPDX-shaped licence identifier (`Word-N.N`, optional `-or-later` or
   `-only`) equals the viewer's grant, and no capitalised word stands
   directly before "licence"/"license". The test names no other licence;
   its patterns are generic.
4. **The test pins the literal date.** As for 0.7.0 and 0.7.1,
   `test_the_manual_states_the_release` pins `'0.8.0 — 5 October 2026'`,
   `'Machinome 0.8.0'`, `'viewer API 29'` (now equal to the declaration,
   so it is compared with `package.json` rather than written as a
   literal), version `0.8.0` and the README's mention. The two tests that
   pinned the API 28/29 work as current source (`..._as_current_source`,
   `..._on_demand_clocked_...`) are repointed to the 0.8.0 section and the
   pages' release wording; the first is renamed to say it is part of the
   0.8.0 release. The `Unreleased`-tolerant structure stays, so the next
   change can write its bullet when it lands.
5. **The bundle is rebuilt in the worktree from the linked
   dependencies.** The banner reads `package.json`'s version at build
   time; `npm run build` reads the linked `node_modules` and writes only
   `dist/`. `npm ci`, `npm install` and `scripts/check-dist` run only in
   the primary checkout after integration.
6. **The release record is new, not appended.** `workflow/release-0.8.md`
   follows `release-0.7.md`'s shape: the release set (machinome 0.8.0 and
   machinome-viewer 0.8.0, each under the licence its own manual states;
   machinome-mechanics 0.1.0 unchanged and not re-released), the release
   order, how packaging is reproduced, and what remains the pilot's.
   `release-0.7.md` stays as written; the README and `workflow/README.md`
   point at the new record.

## Risks / Trade-offs

- [The release date slips past 5 October] → the date is in
  `CHANGELOG.md`, `docs/index.rst`, `workflow/release-0.8.md` and
  `tests/test_documentation.py`, and in the framework's `docs/conf.py`;
  the three manuals must move together.
- [The generic licence patterns refuse a future legitimate sentence, such
  as a third-party notice on a page] → the reader pages carry no
  third-party licence name today; a page that must name one is a decision
  for the pilot, and the test's failure says which page and which word.
- [The changelog section claims something the source does not do] → each
  bullet is checked against the archived change's spec delta and the
  handle reference before writing, and the documentation test still pins
  the members on the reference pages.

## Spec scope

Two specs change, as in 0.7.1: `user-documentation` (the release facts,
the 0.7.1 section kept as released, film annotations as part of 0.8.0)
and `viewer-distribution`, whose "Installed viewer support includes
retained time drives" names the version package, widget and banner carry
and moves from 0.7.1 to 0.8.0. The brief first said to touch no spec but
`user-documentation`; the orchestrator ratified the second delta on
5 October 2026, since a ratified requirement contradicting the shipped
version is worse than a two-line delta. The orchestrator also ratified
rewriting all six licensing sentences, the four the brief did not list
included.
