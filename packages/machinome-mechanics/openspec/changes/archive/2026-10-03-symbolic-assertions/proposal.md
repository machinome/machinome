## Why

Machinome's 0.8 campaign line (cycle `expression-type`) gives the core its
own symbolic type, `machinome.expression_graph.GraphValue`, no longer derived
from solid2's `OpenSCADConstant`, and publishes one predicate,
`machinome.expression_graph.symbolic(value)`, that returns a value's
expression node when it is symbolic and `None` otherwise. This package's
library code is unaffected, but nine of its test assertions spell "the
realized law stayed symbolic" as `isinstance(result, OpenSCADConstant)`:
against that line they fail with a correct symbolic result in hand
(`9 failed, 200 passed, 16 subtests passed`). The assertion names a
modelling library's class instead of the property it means.

## What Changes

- The two symbolic-type assertion sites, `tests/test_motion.py` (the
  realized motion law) and `tests/test_mechanisms.py` (every nonlinear law
  under a symbolic driver, eight subtests), assert
  `symbolic(result) is not None` through the framework's predicate.
- Those two test modules stop importing `OpenSCADConstant`.
- `CHANGELOG.md` gains an `## Unreleased` section recording it, and the
  documentation test that pins the current release reads the newest release
  section past it instead of refusing it (found while applying).
- Nothing else changes: no helper, signature, formula, documentation page or
  dependency line. The tests keep `solid2.get_animation_time()` as their
  symbolic time.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: the requirement that one formula computes numbers and builds
  a deferred expression gains a scenario saying how "symbolic" is observed:
  by the framework's own predicate, not by a modelling library's type.

## Impact

`tests/test_motion.py`, `tests/test_mechanisms.py`,
`tests/test_documentation.py`, `CHANGELOG.md`, the
`mechanisms` baseline spec. The branch `v0.8` targets the framework's 0.8
line; the predicate does not exist in released Machinome 0.7.1, so this
change lives only on that branch until the release pass. Against an
unmodified 0.7 framework the two sites would fail on the import, which is
the reason the branch exists.
