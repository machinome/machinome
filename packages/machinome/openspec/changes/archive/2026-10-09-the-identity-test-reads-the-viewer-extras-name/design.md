## Context

`test_distribution_import_command_and_extras_share_the_name` compares each
of the `viewer`, `mechanics` and `studio` extras with a one-item list of the
bare product name. Since 8 October 2026 the `viewer` extra is
`["machinome-viewer>=0.8.0"]`, so the comparison fails on the floor rather
than on the name. The floor is held to `docs/conf.py`'s `viewer_version` by
`test_the_viewer_extras_floor_at_the_matching_viewer` in
`tests/test_release_records.py`; the identity test has no reason to restate
it.

## Goals / Non-Goals

**Goals:** the identity test asserts the name each extra selects and that
it selects exactly one requirement; it is green on the floored extras and
would still fail on a renamed product.

**Non-Goals:** no change to `pyproject.toml`, to the floor or to the test
that holds it; the `web-snapshot` extra stays out of the identity test, as
it was.

## Decisions

1. **Parse with `packaging.requirements.Requirement`.** `packaging` 26.3 is
   importable in the workspace venv, arrives in the development install
   through `pytest`, and `tests/test_kernel_extras.py` already imports
   `Requirement` the same way. Its `.name` is the distribution name before
   any extras bracket, specifier or marker. Alternative considered: a split
   on `[`, `>`, `<`, `=`, `~`, `!`, `;` and whitespace; rejected as a
   hand-written grammar where the standard parser is already a test
   dependency.
2. **Exactly one requirement per extra stays asserted** by unpacking the
   list into one item, so an extra that gains a second requirement still
   fails here.

## Risks / Trade-offs

- [The test now accepts any version specifier on `mechanics` or `studio`]
  → intended: their versions are not this test's subject, and the name
  remains pinned.
