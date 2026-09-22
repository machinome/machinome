# Verification — 2026-09-22

Originating finding: the Curta Type I 3× project's
`CounterOperatingFixtureTest.test_installed_trial_matches_measured_parts_and_preserves_initial_bank`
failed reproducibly in `FusionNode.shape()` because a stale exact leaf's
`shape()` returned the SCAD `_ArtifactImport` stored in `model`.

Before the source change, the isolated regression
`ExactArtifactTest.test_exact_fusion_recovers_native_leaf_after_brep_goes_stale`
failed at the same `_ArtifactImport.wrapped` access. Its stale artifact is
inside the framework test's temporary build directory.

After the correction:

- `tests/test_exact_geometry.py`, `tests/test_exact_placement_cache.py`, and
  `tests/test_node_scoped_currency.py`: 82 passed.
- `tests/test_step_node.py` and `tests/test_build123d_adapter.py`: 72 passed,
  6 subtests passed, four existing build123d deprecation warnings.
- The originating Curta fixture, run with this worktree first on `PYTHONPATH`:
  one test passed in 46.586 seconds. Its model was not edited and its existing
  build cache was not deleted.

The current-BREP test continues to assert that `render()` is not called when
the artifact is current. This correction changes only the stale path. No
viewer code or public format changed.

The modified exact-geometry requirement was synced to the baseline spec;
OpenSpec strict validation passed for the change and all 34 baseline specs.
No new ADR is needed: the correction enforces the existing separation of
native shape and SCAD presentation described in the architecture and ADR-047.
