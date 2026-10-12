# Release-with-0.7 evidence

Planning commit `eebd44c`. Worktree `WTs/release-with-0-7` on `main`
`842a9a7`, workspace Python 3.12 with the editable framework at 0.7.0
(`e6a42c8`), OPENBLAS_NUM_THREADS=1 / OMP_NUM_THREADS=1.

## Red first

The three new documentation tests failed on the unchanged text:
`test_the_manual_states_the_release` on "in preparation for release" in
`docs/index.rst`; `test_the_manual_links_existing_framework_pages` on
`declaring.html`, `driving.html`, `quickstart.html` and `testing.html`;
`test_the_reference_names_no_consumer_projects` on 22 project names across
the reference pages, README and getting-started page.

## Green

- `python -m pytest -q`: 201 passed, 24 subtests passed, 1.93 s (198 before
  the cycle plus the three new tests).
- Strict HTML `sphinx -b html -n -W --keep-going`: clean.
- Doctests `sphinx -b doctest -W --keep-going`: 10 documents, 151 tests,
  0 failures. Two type-only doctests over `solid2` internals were replaced
  by code blocks in the framework's spelling; every value-asserting example
  is unchanged.
- Every framework link (`index`, `start/install`, `concepts/relations`,
  `concepts/values`, `reference/assertions`, `project/upgrading`) resolves
  to a file in the built Machinome 0.7 manual at framework `e6a42c8`.
- `python scripts/check-dist`: wheel and sdist built, metadata validated,
  installed numeric/symbolic smoke passed outside the checkout; nothing
  uploaded.
- `git diff --check` clean; change and baseline specs validate strict.

## Companion correction in the framework

The framework manual said "twelve" helpers on four pages and told readers
to follow source installation "while publication is pending"; corrected in
the framework repository (api, install, manuals, upgrading, changelog
pages), strict build clean.

## Out of scope, found while applying

- The package docstring in `machinome_mechanics/__init__.py` says
  "Thirteen `kinematics.py` files in this workspace", a sentence about the
  development workspace visible through `help()`. Not a manual page; left
  for a code cycle.
- The viewer's changelog dates its 0.7.0 release 21 September 2026 while
  the framework's release date is 20 September 2026. This package uses the
  framework's date. The pilot may want the viewer's to match.
