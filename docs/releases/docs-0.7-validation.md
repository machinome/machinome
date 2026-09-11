# 0.7 documentation refresh — validation record

This is maintainer release-preparation work, not a release announcement.

## Scope and provenance

- Framework base: `2bdc50b37be920e79202d1c9e9c5700e43f525e0`.
- Isolated branch/worktree: `docs-0-7`.
- The pilot approved a direct documentation refresh on that committed base,
  leaving the primary checkout's existing workflow edits alone, and then
  requested an amendment to restore the original teaching progression.
- The tutorial builds upon the framework's existing disc, pointer and pin
  example: model parts, assemble them, animate the pointer, test its fit,
  then introduce declarative parameters, joints and drivers.
- The rejected Clock 01 tutorial implementation, geometry wrapper, tests,
  package configuration, LICENSE and NOTICE have been removed. No
  3DPrintedClocks design source is copied or reimplemented in the tutorial.
- V8, Metamaquina 2 and Clock 01 are three sibling external examples, each
  with a source link and a live model. Their source remains in independent
  repositories tracked through Git submodule references, not framework
  source files. Viewer exports are generated during the documentation build.
- Clock 01 credits Luke Wallin's original
  [3DPrintedClocks](https://github.com/MrBunsy/3DPrintedClocks) project.
  Its separate example page links the external licence and briefly explains
  the source-distribution obligation.
- The framework and its own tutorial source remain Apache-2.0. The
  independent viewer is AGPL-3.0-only; external designs retain their own
  licences.

The refresh covers the introduction, learning path, assembly/motion/time
tutorials, migration guide, user-facing release notes, examples, reference
corrections and both documentation builders. The former unreleased engineering
changelog is preserved in `development-0.7.rst`, explicitly labelled as
intermediate development history. The only framework source edit corrects
reStructuredText in the Orbit docstring; no runtime behaviour changes.

## External source revisions

The documentation uses existing committed v0.7 migrations from the independent
project repositories. Their older public revisions still import ports from
the old module and cannot export with this framework base.

| Example | Pinned source commit |
| --- | --- |
| V8 engine | `a25b0749a34a1594dbcbef1aa38acc4835c2ff6e` |
| Metamaquina 2 | `b77d67cfdaf36a3ec110ba065af72a39f75931cb` |
| Clock 01 | `0e496374716f03f1ab8026179088e7b14a9cb8fc` |

These commits were fetched locally from the workspace's independent project
repositories for validation. They were not pushed by this change and were
not on the configured public branches at validation time. Making these exact
revisions available from the configured submodule remotes is a prerequisite
for a fresh public checkout, CI and Read the Docs. No project source or
pre-existing project edits were changed or committed by this work.

## Validation

Run from the framework worktree with the workspace environment and this
worktree on PYTHONPATH:

- `sphinx-build -E -b html -W --keep-going docs docs/_build/html`:
  clean full build, including all three live external examples and the
  original small tutorial embeds.
- `pytest -q tests/test_docs_exports.py tests/test_sphinx_ext.py
  tests/test_time_base.py tests/test_joints.py`:
  **192 passed, 278 subtests passed**. One expected FutureWarning exercises
  the legacy render-time compatibility path.
- New documentation regression checks failed before the correction, then
  passed after restoring the sibling example pages and framework-owned
  tutorial progression. Existing checks verify export coverage in both
  CI and Read the Docs and one external model per example page.
- README parsed independently with docutils, warnings treated as errors.
- `git diff --check`: clean.

Each external model exported successfully from its own submodule directory:

- V8: `solid export -o docs/_exports/v8-engine`.
- Metamaquina 2: `solid export -o docs/_exports/metamaquina2`.
- Clock 01: `solid export -o docs/_exports/clock01 wall_clock_01`.

These were real CAD builds, not mock geometry. Browser inspection of the
three example pages found a rendered model in each, with no JavaScript
errors; screenshots of all three were inspected. The restored assembly
lesson also rendered its three small embedded models. Generated exports
and screenshots are not committed.

The restored pin-fit exercise was executed through `solid test` in a
temporary project outside the repository:

1. Deliberately oversized pin (radius 3.1): both fit assertions failed.
2. Clearance at rest (radius 2.99): both passed.
3. The same coarse geometry swept over 16 instants: pointer fit failed.
4. Fine tessellation (`fn = 256`): both 16-instant sweeps passed.

This checks the lesson's red/green progression, including the difference
between a fit at rest and clearance throughout motion. The new joint lesson
was also evaluated numerically: a quarter timeline turn and a manual
driver setting each produced -90 degrees; a 0.5 follower relation produced
-90 degrees from a -180-degree input.

## Limits and release prerequisites

Exporting and inspecting an external example is not a complete mechanical
test suite, a dynamics validation or a manufacturing certification. This
documentation change did not run or certify every external model's full
geometric test suite.

The installed viewer reports API 7, package 0.1.0, supporting schemas 1–4.
That package is not yet published. Public CI and Read the Docs require
the matching viewer source and all three pinned example revisions to be
available remotely; viewer source installation remains explicit in their
configuration. Release installation commands are labelled as future commands
until 0.7 and the viewer are published.

No package version, release tag, remote branch, PR or publication was changed.
Integration into the primary branch remains the pilot's decision.
