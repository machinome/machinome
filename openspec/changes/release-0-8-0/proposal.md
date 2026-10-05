## Why

Machinome 0.7.1 is at released state on `main`, dated 27 September 2026.
Since then `main` has taken the whole first layer of the lean-core
campaign (`workflow/ongoing/lean-core.md`, "Layer 1 complete; the root is
clean"): ten cycles that make a bare install the core alone, give every
name one address, name the two comparison engines for what they consume
and make the OpenSCAD family one node package among the others, plus
production profiles, the verdict store, the export's revision record, a
clocked simulation's identity and a correction for a project reached
through a symbolic link (ADR-156 to ADR-181). The manual still describes
all of it as unreleased: fifteen bullets in the changelog's `Unreleased`
section, three *(unreleased)* sections on the upgrading page, and a status
page that says 0.7.1. On 5 October 2026 the pilot decided to release it as
**Machinome 0.8.0**, the release state made that day, with the upload
left to the pilot as it was for 0.7.1. The pilot also decided that from
this release Machinome is licensed **GPL-2.0-or-later or
CERN-OHL-S-2.0-or-later, at the recipient's choice**.

## What Changes

- **The version is 0.8.0.** `pyproject.toml`, `machinome/__init__.py`,
  `machinome/vet/universe.toml`, `setup.cfg` and `docs/conf.py`'s `release`
  move together, as `setup.cfg`'s bumpversion table names them, by hand
  (bumpversion commits and tags). `version` becomes `'0.8'` and
  `release_date` `'5 October 2026'`. `document_versions` stays `'1 to 13'`
  and `mechanics_version` `'0.1.0'`: nothing in 0.8 moves the published
  document (the export's `source` record is additive and moves no version).
- **The matching viewer, provisionally 0.8.0, API 29.** The viewer's own
  main carries unreleased work above 0.7.1 (on-demand capture of a clocked
  machine, API 29), so a viewer 0.8.0 released from it is not 0.7.1
  renumbered. `docs/conf.py` states `viewer_version = '0.8.0'` and
  `viewer_api = '29'` and `context7.json` the same; the viewer's number
  and API are the pilot's open choice and live in `docs/conf.py` and
  `context7.json` only, so the choice flips in one edit each (keeping the
  viewer at 0.7.1 would also retire the one test that holds the viewer
  numbered with the framework). No page states the viewer's number except
  through its substitution.
- **The licence is stated as a fact, once.** `docs/conf.py` gains
  `framework_licence = 'GPL-2.0-or-later or CERN-OHL-S-2.0-or-later'`,
  exposed as `|framework_licence|`; every manual page that states the
  framework's licence uses it (`start/install.rst`, `why.rst`,
  `project/status.rst`); `README.rst` states the same words literally and a
  test holds it to `conf.py`. The viewer stays a separate
  AGPL-3.0-or-later package. `machinome-mechanics` is described without
  stating its licence, on the sibling manuals page and in
  `docs/architecture.md`; its own manual states it. The licence is stated as the current fact and
  nothing more: no earlier licence is named anywhere this change writes,
  no "was" or "formerly", no position on derivative works, no exception
  text, no compatibility claim, no reason. The changelog reads as if it
  had never carried another licence: its one older sentence naming an
  earlier licence (in the 0.4 section's packaging list) is rewritten
  minimally to name none, the one edit this change makes to an older
  changelog section.
- **The licence instruments are not this change's.** `LICENSE`, `NOTICE`,
  `pyproject.toml`'s `license` field and classifiers, every
  `SPDX-License-Identifier` header (under `machinome/`, `tests/`, `tools/`
  and `docs/conf.py`'s own), the `framework-identity` spec's scenarios,
  `AI-USE.md`, `CREDITS.md`, and the 0.7.x and older sections of
  `HISTORY.rst` are changed by another agent, in a separate commit the
  pilot injects into the history. This division of labour exists: the
  manual states the licence 0.8 ships under, and the instruments that
  grant it arrive in that commit, so at this change's commits the two do
  not yet agree, by design. `workflow/ongoing/release-0.8.0.md` lists
  those instruments, by file and count, for that commit's author.
- **The records describe 0.8.0 as released.** The changelog's
  `Unreleased` section becomes `Machinome 0.8.0`, released on 05/Oct/2026,
  rewritten as a story for readers: what a maker gets, the licence first,
  a "Breaking changes" paragraph listing every breaking change in one line
  and sending the reader to the upgrading page, then the families in the
  order a maker meets them, each bullet keeping its *Breaking* paragraphs
  and describing the code as it stands at 0.8.0 (several bullets were
  written mid-campaign and name addresses a later cycle moved).
  `HISTORY.rst` gains `Machinome 0.8.0 (2026-10-05)`. The status page
  describes 0.8.0 and its direction as fact. `README.rst` gains a 0.8
  paragraph, the licence and the release-note link. `docs/architecture.md`'s
  one sentence giving the framework's licence states the new one.
  `context7.json` states 0.8.0 and rewrites its engine and OpenSCAD rules.
- **A release note for 0.8**, `docs/releases/release-0.8.rst`, reached from
  the changelog's toctree beside `release-0.7.rst`: the one case where a
  new page is right.
- **The upgrading page opens with "Upgrading from Machinome 0.7 to 0.8"**:
  every breaking change of 0.8 with what to change, each checked against
  the code; the three *(unreleased)* sections lose their marker and are
  folded under it; the 0.6 to 0.7 material stays below, intact.
- **Tests pin the release by `pyproject.toml`'s version**, as since 0.7.1:
  the release-note test derives the page from the version's major.minor;
  the licence pins are new (the substitution; no licence identifier
  spelled literally on a page under `docs/` outside the historical
  release notes but the viewer's; `README.rst` spelling only the
  viewer's and `conf.py`'s words);
  the tests that read the `Unreleased` section or pin the 0.7.1 identity
  are repointed to the 0.8.0 section.
- **No source, document or behaviour change.** Every capability described
  is already on `main`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: a new requirement, "The 0.8.0 release is
  recorded": where the release facts live and that they agree, the licence
  stated through `conf.py`'s one fact and matched by `README.rst`, the
  release note, and the upgrading page listing every breaking change of
  0.8. "The 0.7.1 release is recorded" stops requiring 0.7.1 to be the top
  entry, the status page's version and `context7.json`'s, which 0.8.0
  supersedes, and keeps its section, history entry and release-note
  section as released. "The manual imports every name from its module"
  records the change in the 0.8.0 section instead of an unreleased one.
  "The viewer's provenance and installation are stated" says a framework
  installation without the viewer snapshots through OpenSCAD with the
  `openscad` extra, as 0.8 requires. No other spec changes;
  `framework-identity` belongs to the licence commit.

## Impact

`pyproject.toml` (version only), `setup.cfg`, `machinome/__init__.py`,
`machinome/vet/universe.toml`, `docs/conf.py` (release block),
`docs/project/changelog.rst` (the 0.8.0 section, and one sentence of
the 0.4 section), `docs/project/status.rst`,
`docs/project/upgrading.rst`, `docs/releases/release-0.8.rst` (new),
`docs/start/install.rst`, `docs/why.rst`, `docs/reference/manuals.rst`
(the mechanics entry), `docs/architecture.md` (the framework's licence
sentence and one word of the mechanics sentence), `HISTORY.rst`,
`README.rst`, `context7.json`, `workflow/ongoing/release-0.8.0.md` (new),
`workflow/ongoing/lean-core.md` (one closing paragraph); tests
`test_release_records.py`, `test_docs_structure.py`,
`test_machinome_identity.py`, `test_profile_documentation.py`,
`test_production_documentation.py`.

Outside the framework and not this change's: the licence commit; the
viewer's own release in its repository; the studio's `machinome_test` tool
and skills and the workspace's simulate-project skill, which still pass the
former engine flags; machinome-mechanics and machinome-freecad. The tag,
the push, the upload, Read the Docs and Context7 remain the pilot's, and
no distribution is built, because the licence commit changes the files a
distribution carries.

Standalone cycle on framework `main` base `3435b35`, branch and worktree
`release-0-8-0` at `machinome/WTs/release-0-8-0`, integration target
framework `main`.
