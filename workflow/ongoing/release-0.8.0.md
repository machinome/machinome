# Machinome 0.8.0: release handoff

Status: working record, 5 October 2026, written by the OpenSpec change
`release-0-8-0` (bench `release-0-8-0`, base 3435b35), which integrates
into framework `main` by fast-forward after the full suite. Not ratified;
the change's archive is the authority for what was released. This note says
what the release state checked and what remains, for the pilot and for the
agent that changes the licence instruments.

## What the release state is

Version 0.8.0 in the five files of `setup.cfg`'s bumpversion table, dated
5 October 2026 in `docs/conf.py`'s release block. The manual describes 0.8.0
as released: the changelog's `Machinome 0.8.0` section, `HISTORY.rst`, the
release note `docs/releases/release-0.8.rst`, the status page, the upgrading
page's "Upgrading from Machinome 0.7 to 0.8" part, `README.rst` and
`context7.json`. The framework's licence is stated as GPL-2.0-or-later or
CERN-OHL-S-2.0-or-later, at the recipient's choice, through one fact,
`framework_licence` in `docs/conf.py`; `README.rst` states the same words and
a test holds it to that fact.

The matching viewer is provisional: `docs/conf.py` says `viewer_version =
'0.8.0'` and `viewer_api = '29'`, and `context7.json` the same, because the
viewer's main carries unreleased API 29 above 0.7.1. Whether the viewer
releases as 0.8.0 (API 29) or stays 0.7.1 (API 27) is the pilot's choice; it
lives in those two files only. Keeping 0.7.1 also retires
`tests/test_release_records.py::VersionFilesTest::test_the_matching_viewer_is_numbered_with_the_framework`.
No other page or record states the viewer's number: the changelog, the
release note and `HISTORY.rst` say only that exports keep document versions
1 to 13, which holds either way.

## (a) The licence instruments this change did not touch

Changed by another agent, in a separate commit the pilot injects into the
history. Counts taken by grep on the bench at 3435b35.

| Instrument | Count |
|---|---|
| `LICENSE` | 1 file, 202 lines |
| `NOTICE` | 1 file, 2 lines |
| `pyproject.toml` `[project] license` field | 1 line (line 11) |
| `pyproject.toml` licence classifiers | 0 (none declared) |
| `SPDX-License-Identifier` headers under `machinome/` | 103 files |
| `SPDX-License-Identifier` headers under `tests/` | 532 files |
| `SPDX-License-Identifier` headers under `tools/` | 7 files |
| `SPDX-License-Identifier` header of `docs/conf.py` | 1 file |
| `SPDX-License-Identifier` headers under `openspec/changes/archive/` (evidence scripts) | 32 files |
| `SPDX-License-Identifier` headers under `workflow/archive/` | 1 file |
| `openspec/specs/framework-identity/spec.md` scenarios naming the framework's licence | 2 (lines 96–97 and 103) |
| `CREDITS.md` sentence stating the project's licence | 1 (line 5) |
| `AI-USE.md` sentence stating the repository's licence | 1 (line 86) |

Python files with no header at all: 16 of 118 under `machinome/`, 52 of 584
under `tests/`, 3 of 10 under `tools/`.

**Files created by the 0.8 cycles.** Between v0.7.1 and 3435b35 the cycles
added 15 files under `machinome/` and 75 under `tests/` that carry a header.
A commit injected into the history before those cycles reaches none of them:
they need their headers changed at the tip (or the injected commit's change
replayed there) as well.

**Not instruments.** The ADRs under `docs/adrs/`, the archived OpenSpec
changes and the release notes of 0.7 and older under `docs/releases/` are
records and keep the words they were written with. The 0.7.x and older
sections of `HISTORY.rst` were not touched.

## (b) The pilot's steps

1. The licence commit, injected into the history (see (a)).
2. The `v0.8.0` tag, at the commit that carries both the release state and
   the licence instruments.
3. The push of `main` and the tag.
4. The upload to PyPI, from distributions built fresh at the tagged commit.
5. The Read the Docs build of `latest` and the `v0.8.0` version.
6. The Context7 refresh from `context7.json`.
7. The viewer's choice (0.8.0 at API 29, or 0.7.1 kept), its own release
   change in its repository, its tag, push and upload; and, if the viewer
   stays 0.7.1, the edit of `docs/conf.py` and `context7.json` and the
   retirement of the one test named above.

## (c) Follow-ups outside the framework

From the campaign plan's last section (`workflow/ongoing/lean-core.md`):

- machinome-studio: the `machinome_test` tool (`floor/mcp_server.py`) and its
  two skills still pass the former engine flags and the former test variable,
  and teach the node root's former spelling.
- The workspace's `skills/simulate-project/SKILL.md` spells the former mesh
  flag.
- machinome-mechanics: two tests and two examples import from the node root,
  and twelve test files take the animation time from SolidPython rather than
  `self.time` in `simulate()`.
- machinome-freecad: its retarget onto `BrepLeafNode` and leaf contract 3.
- Every checkout that pulled the development line needs
  `git clean -fdX machinome/occt machinome/manifold machinome/openscad` once,
  for the deleted packages' `__pycache__`. A checkout at 0.7.1 never had them.
- Deferred past 0.8 by the pilot: the viewer seam, with ADR-179's provisional
  renderer column shipping.

## (d) Distributions not built

No wheel or sdist was built and `check-dist` was not run: the licence commit
changes `LICENSE`, `NOTICE`, `pyproject.toml`'s metadata and the headers of
files a distribution carries, so a distribution built before it would carry
the wrong instruments. Build them at the tagged commit, after the licence
commit.

## What was checked

The release-records, documentation-structure, identity, profile, production,
frame-precision, mates, tutorial, Sphinx-extension and node-root tests, and
the strict Sphinx build; the pages read in the built HTML are listed in the
change's `evidence.md`. The full suite is the orchestrator's run before the
change is archived.
