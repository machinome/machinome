## Context

The framework's 0.8 campaign line takes OpenSCAD out of the core. Its cycle
`expression-type` (framework bench `machinome/WTs/v0.8-expression-type`,
applied and not yet committed when this change was cut, 3 October 2026)
makes `GraphValue` the core's own type instead of a subclass of solid2's
`OpenSCADConstant`, and publishes `machinome.expression_graph.symbolic(value)`:
the value's `ExpressionNode` when it is symbolic, `None` otherwise. A plain
`int` or `float` is never symbolic; a `GraphValue` or `ExpressionNode` always
is; any other value is symbolic when the core's OpenSCAD engine adopts it,
which is how a value SolidPython built is still recognised.

This package's helpers are compositions over `machinome.math` and are
unaffected. Its tests are not: `tests/test_motion.py:46` and
`tests/test_mechanisms.py:349` assert `isinstance(..., OpenSCADConstant)`.
Against the bench the suite reads `9 failed, 200 passed, 16 subtests passed`
(the motion test and eight subtests, one per nonlinear law); against the
released framework it read `201 passed, 24 subtests passed`.

Probed against the bench under the suite's own command: the realized
slider-crank law and the eight nonlinear laws return `GraphValue`s; the four
linear laws (`meshed_angle`, `driving_angle`, `screw_travel`,
`screw_angle`) applied to solid2's animation time still return solid2's
`OpenSCADConstant`, because their arithmetic never leaves SolidPython. The
predicate answers "symbolic" for all thirteen.

## Goals / Non-Goals

**Goals:**

- The two assertion sites say what they mean, "the result stayed symbolic",
  in the framework's public spelling, and pass on the 0.8 line with the
  values they already produce.

**Non-Goals:**

- Any change to a helper, signature, formula or manual page.
- Replacing `solid2.get_animation_time()` in the tests (see Deferred).
- Moving the dependency line `machinome>=0.7.0` (see Decisions).

## Decisions

- **The framework's predicate, not another type check.** `symbolic(x) is not
  None` is the framework's own definition of "symbolic" and the one its core
  uses. Alternatives: `isinstance(x, GraphValue)` would fail the four linear
  laws, whose results are solid2 values the core adopts, and would tie the
  tests to a second class name the framework may change again;
  `isinstance(x, (OpenSCADConstant, GraphValue))` keeps naming a modelling
  library's class for a property the framework now owns.
- **Only the assertions change.** The surrounding checks (`"crank" in
  str(result)`, the emitted-builtins check through `_expanded`) already read
  the expression text and pass on the bench once the type check no longer
  stops them first.
- **The changelog's release pin reads past `Unreleased`.** Found while
  applying: `tests/test_documentation.py::test_the_manual_states_the_release`
  took the first `## ` section of `CHANGELOG.md` as the current release, so
  the `## Unreleased` section this change adds failed it. Under the
  standard's rule the work since a release sits under `Unreleased` until the
  release renames it; a pin that forbids that section is the defect. The pin
  now takes the newest section that is not `Unreleased` and still requires
  it to be 0.1.0 with Machinome 0.7.0. Alternative: leave the changelog
  alone. Rejected: the brief and the standard both ask for the entry.
- **The dependency line stays at `machinome>=0.7.0` in this cycle.** The
  branch `v0.8` targets the framework's 0.8 line, where the predicate exists;
  released 0.7.1 does not have it. The pin moves at the release pass, as the
  0.1 release record (`workflow/release-0.1.md`) states the framework
  companion of each mechanics release; until then `main` remains the 0.7
  line and `v0.8` is not released.

## Risks / Trade-offs

- [The predicate is renamed or moved before 0.8 is released] → the two
  sites fail at import on the `v0.8` branch, loudly; the fix is one import.
- [The branch is installed against Machinome 0.7.x] → the suite fails at
  collection: the two test modules, and the nine per-helper modules that
  import shared fixtures from `tests/test_mechanisms.py`, cannot import the
  predicate (eleven collection errors, found while applying). The library
  itself is unaffected. The branch is a campaign line, not a release.

## Deferred

- The tests use solid2's `get_animation_time()` as their symbolic time (in
  twelve test files). They could use the framework's own symbolic time
  instead, as a later cycle if the pilot wants it; the framework still adopts
  a SolidPython value through its OpenSCAD engine, so nothing forces it now.
- The dependency pin moves to the framework's 0.8 release at the mechanics
  release pass that accompanies it.
