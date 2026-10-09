## Context

`BRepExtrema_DistShapeShape` has two shapes of constructor: the empty one,
after which a caller loads the shapes, sets flags and calls `Perform()`;
and the two-shape one, which performs in the constructor. `_distance` uses
the second and then sets `SetMultiThread(True)`, which has nothing left to
govern. OCP 7.8.1 binds `LoadS1`, `LoadS2`, `SetFlag`, `SetAlgo`,
`SetMultiThread` and `Perform`. Measured on the lock's 730 pairs
(`workflow/ongoing/distance-tier-measurement-2026-10-09/`): 186 s against
33 s, no value differing, the tree algorithm making no difference.

## Goals / Non-Goals

**Goals:** the distance runs threaded; the order is pinned by a test that
does not depend on timing.

**Non-Goals:** no change to the witness, to what `_distance` returns, or to
where it is called; no distance tier.

## Decisions

1. **Empty constructor, load, flag, perform.** The minimum-only flag
   (`Extrema_ExtFlag_MIN`) is set too, since the helper reads only `Value()`;
   the algorithm stays the default, as the tree one measured no faster.
2. **The test records the kernel calls through the module's name.** A
   recorder class patched in for `brep.BRepExtrema_DistShapeShape` logs its
   method calls in order and answers a fixed value; the test asserts that
   `SetMultiThread(True)` precedes `Perform()`. Against the current code the
   recorder's two-argument constructor is called and `Perform` never is, so
   the test is red for the right reason. A second test keeps the value
   honest against CadQuery's `Shape.distance` on two real solids.

## Risks / Trade-offs

- [A threaded extrema answering differently from the single-threaded one]
  → measured on 730 real pairs with no disagreement; the value test pins
  the real kernel.
