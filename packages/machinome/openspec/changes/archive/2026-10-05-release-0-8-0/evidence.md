# Evidence: release-0-8-0

Base `3435b35` (framework `main`, 5 October 2026), branch and worktree
`release-0-8-0` at `machinome/WTs/release-0-8-0`, workspace venv
(`/home/asa/devel/machinome/.venv/bin/python`), `openspec` 1.6.0. Planning
commit `3b2b6b2`.

## Red first

- `tests/test_release_records.py` on the unmodified bench: **9 passed, 57
  subtests passed**, green at 0.7.1.
- After moving the five version statements to 0.8.0 (and `release_date`,
  `viewer_version`, `viewer_api` in `docs/conf.py`), before any record:
  **4 failed, 5 passed** —
  `test_context7_states_the_release` ("'Machinome 0.8.0 (released
  2026-10-05)' not found"), `test_the_changelog_first_release_section_is_the_released_version`
  ("'Machinome 0.7.1' != 'Machinome 0.8.0'"),
  `test_the_history_top_entry_is_the_released_version` ("'0.7.1' !=
  '0.8.0'"), `test_the_release_note_has_the_dated_section` ("'0.8.0' not
  found in '0.7.1: parts placed by relation'"). The version-file tests passed
  because every file moved together.
- `test_the_release_note_has_the_dated_section` repointed to the page of the
  version's major.minor: red, "False is not true :
  docs/releases/release-0.8.rst". `test_context7_states_the_release` now holds
  "The matching viewer is <viewer_version>, API <viewer_api>" to `conf.py`.
- Licence pins in `tests/test_docs_structure.py` (`framework_licence` among the
  substitutions; `LicenceFactTest`): **7 failed, 10 passed** —
  `framework_licence` is no substitution of `conf.py`; a licence identifier
  other than the viewer's spelled on `project/changelog.rst`,
  `project/status.rst`, `reference/manuals.rst`,
  `start/install.rst` and `why.rst`; `README.rst` not stating `conf.py`'s
  `framework_licence` (no such fact yet). The pin names no licence in its own
  code; it matches identifiers by shape and admits only the viewer's
  `AGPL-3.0-or-later` (and, in the README, the words of `framework_licence`).
- `tests/test_production_documentation.py` repointed to the 0.8.0 section:
  red, `IndexError` (no `Machinome 0.8.0` section yet).
- `tests/test_profile_documentation.py` pinned `viewer_api = '27'`; with the
  provisional API 29, `grep -c "viewer_api = '27'" docs/conf.py` is 0, so the
  pin fails; it is relaxed to "at least 27", what the 0.7.0 profile-contact
  record it guards needs.
- `KernelExtrasTest` refused `machinome.node.adapters` on the upgrading page,
  which now lists that address as a breaking change; the page joins the
  changelog in admitting it.

## Green

The named documentation tests, `-p no:cacheprovider`:

    tests/test_release_records.py tests/test_machinome_identity.py
    tests/test_docs_structure.py tests/test_docs_exports.py
    tests/test_viewer_documentation_links.py tests/test_profile_documentation.py
    tests/test_production_documentation.py tests/test_frame_precision_docs.py
    tests/test_mates.py tests/test_tutorial_counter.py tests/test_sphinx_ext.py
    tests/test_node_root_exports_nothing.py
    218 passed, 1339 subtests passed in 77.16s (0:01:17)

`openspec validate user-documentation --type spec --strict` after the sync:
valid.

After the prose revisions of the orchestrator's review (measurements out of
the release section and the release note; the licence requirement stated as
a rule), the same twelve files, `-p no:cacheprovider`:

    218 passed, 1339 subtests passed in 61.53s (0:01:01)

## Full suite

Run by the orchestrator on the bench, on the apply before the prose
revisions (the documentation tests above ran after them):

    4602 passed, 4 skipped, 55 warnings, 6546 subtests passed in 760.73s (0:12:40)

exit 0.

## Build

- `python -m sphinx -b html -W --keep-going -E docs docs/_build/html` (the
  flags CI and Read the Docs use, plus `-E`): exit 0.
- With `-n` as well: 5 warnings, all `reference target not found`
  (`docs/reference/api.rst` lines 187, 199, 230; two `Sim` docstrings in
  `machinome/simulation/sim.py`). The same five, word for word, on a build of
  the base tree 3435b35 (`git archive 3435b35 docs machinome`, built apart);
  none is this change's. Rerun after the prose revisions with
  `-n -W --keep-going -E`: the same five, and nothing else ("build finished
  with problems, 5 warnings (with warnings treated as errors).").

## Probes on the bench (what the records state)

- At 3435b35, by import: `machinome.exact`, `machinome.scad_expression`,
  `machinome.scad_engine`, `machinome.openscad`, `machinome.occt`,
  `machinome.manifold`, `machinome.exact_engine`, `machinome.mesh_engine`,
  `machinome.exact_cache`, `machinome.exact_artifacts`,
  `machinome.node.exact_leaf` raise `ModuleNotFoundError`;
  `machinome.node.adapters` and `machinome.node.adapters.step` raise the
  dissolution's `ImportError`; `from machinome.node import AssemblyNode`
  raises the root's `ImportError` naming `machinome.node.assembly`;
  `SymbolicTruthError.__mro__` is `(SymbolicTruthError, Exception, ...)`;
  `AssemblyNode` has no `scad_code` (the publishing page's "for any node, is
  its `scad_code`" was stale and now names `scad_code(node)` in
  `machinome.node.openscad.writer`).
- At v0.7.1, by `git show`/`git ls-tree`: `machinome/exact.py` (with
  `ExactCommonInconsistency`, `ExactCommonVerificationError`),
  `machinome/mesh_engine.py`, `machinome/openscad.py` (`require_openscad`,
  `openscad_binary`, `OpenScadUnavailable`), `machinome/scad_expression.py`,
  `machinome/node/exact_leaf.py`, `machinome/node/adapters/*`,
  `--exact`/`--faceted`/`SOLID_TEST_KERNEL`, a node's `exact` flag, the
  underscored sheet hooks, `Builder(scad_output=)`, `OPENSCAD_FOV` and
  `scad_expression` in `core/expressions.py`; no kernel extras (every kernel
  required). `machinome.occt`, `machinome.manifold`, `machinome.exact_engine`,
  `exact_cache`, `exact_artifacts`, `machinome.scad_engine` and the extras
  `occt`/`manifold` existed only on the development line and are not in any
  release: the 0.7 to 0.8 table on the upgrading page maps the 0.7.1 names.
- Document versions: `machinome/core/serializer.py` tops at 13 and is
  unchanged in version constants since v0.7.1; `export.py` gained only the
  additive `source` record.
- `machinome snapshot`'s default renderer is the `openscad` row of
  `machinome.node.supported`, refused without `machinome[openscad]` naming the
  extra and `--renderer web`, and runs the OpenSCAD executable.
- The merge: `3435b35` has parents `9fb85e2` (main) and `8d81141` (the line);
  `main` took 86a654e, d1efb70 and 9fb85e2 after the fork, each touching
  `workflow/` only.

## Read as a reader

In the built HTML: `project/status`, `project/changelog` (the 0.8.0 section),
`project/upgrading` (the 0.7 to 0.8 part and its three sections),
`start/install` ("Two packages, two licences", "Upgrading") and
`releases/release-0.8`. Two link texts read badly through the page's new
title ("Upgrading from Machinome 0.7 to 0.8 lists what changed from 0.7 to
0.8"; "each with what to change on Upgrading from Machinome 0.7 to 0.8") and
were given explicit texts; two list items of the upgrading page carried a
literal inside bold, which reStructuredText leaves unrendered, and were
reworded (one in `HISTORY.rst` likewise).

## ADR disposition

None. A release records what is on `main` and decides no architecture; no
ADR is added or amended.

## Left to the pilot

Archived with the spec update skipped, the main spec having been synced by
hand. The licence commit, the
viewer's number, integration, the tag, the push, the upload, Read the Docs,
Context7: `workflow/ongoing/release-0.8.0.md`.
