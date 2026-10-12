# symbolic-assertions evidence

Planning commit `a31f005`. Worktree `WTs/v0.8-symbolic-assertions` on branch
`v0.8` (from `main` `5fdf732`), workspace Python 3.12.3. Framework: the bench
`machinome/WTs/v0.8-expression-type` at `2c9d65f` with the `expression-type`
change applied and uncommitted, 3 October 2026. Command:
`env -C <wt> PYTHONPATH=<bench>:<wt> python -m pytest -q -p no:cacheprovider`;
`machinome.__file__` resolved inside the bench and `machinome_mechanics.__file__`
inside the worktree.

## Red first

Against the bench before the change:
`9 failed, 200 passed, 16 subtests passed in 2.01s` — `tests/test_motion.py::
test_the_realized_law_preserves_symbolic_math` (`isinstance(<ExpressionNode
binop '+'>, OpenSCADConstant)` false: the result is a `GraphValue`) and
`tests/test_mechanisms.py::SymbolicFaceTest::test_a_law_rides_through_a_symbolic_driver`
for `crank_pin`, `crank_rod_angle`, `piston_height`, `delta_carriage`,
`delta_rod`, `circle_intersection`, `triangle_angle`, `link_rise`.

The added `## Unreleased` changelog section then failed
`tests/test_documentation.py::test_the_manual_states_the_release`
(`1 failed, 200 passed, 24 subtests passed in 1.86s`), which took the first
section as the current release; the pin now reads past `Unreleased`.

## Green

Against the bench after the change:
`201 passed, 24 subtests passed in 1.87s`. `git diff --check` clean; no
`OpenSCADConstant` remains under `tests/`.

A probe under the same command showed `symbolic()` answering "symbolic" for
the realized motion law, the eight nonlinear laws (`GraphValue`) and the four
linear laws (`meshed_angle`, `driving_angle`, `screw_travel`, `screw_angle`),
which still return solid2's `OpenSCADConstant` when fed solid2's animation
time.

## Against the primary framework checkout

For comparison, `PYTHONPATH=machinome:<wt>` (framework `main` `feb23f2`,
without `expression-type`): collection stops with 11 errors,
`cannot import name 'symbolic' from 'machinome.expression_graph'` — the two
changed modules and the nine per-helper modules that import fixtures from
`tests/test_mechanisms.py`. Expected: the branch targets the 0.8 line.
