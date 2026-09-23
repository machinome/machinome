## Context

`OperatingCurta` now has a retained radial positioning ball declared by Follow and two matching dynamic Bounds. On its production graph each Bound's subprogram is the same two deterministic compiled laws followed by the same terminal Follow. Each Bound searches 64 uniform fractions plus the existing Follow cut sides and any bisection points. A five-tick no-mesh run at the project source hashes below took 37.1779 CPU seconds; the static-ball control took 4.5545. cProfile attributes 81.7 of 93.5 profiled CPU seconds to searched constraints and records 768 full prefix subprogram replays, most recomputing Follow partitions. This is a replay duplicate, not a need to alter the search or the machine.

Frozen empirical caller: project `a139fe0`, with uncommitted production adoption and `simulation/running.py` SHA-256 `337f3ae77b70d5e5138787a706b6bb8f528001d4102c2bfdf4b52f5fb47d800f`, `simulation/positioning.py` `2c757f98f9bcde3d55430f0fd1cb1a4a8567940628313faf56e28002554ea2a5`, `simulation/positioning_ball_trial.py` `e90dc76db2b15d5dbe3f0ab1f8344f2ddf48f9d7194c7aa199b6ae03b9925b97`, and `simulation/positioning_ball_profiles.py` `cf0382d6cea269bff7c66dfdf8651bd857f5457396ffec80778fe6ca7d591af4`. Framework base `83aad09` includes Follow `f4c48f6`; primary untracked user files remain untouched.

## Goals / Non-Goals

**Goals:** One search stretch can reuse a *successful* prefix propagation when the other matching Follow Bound asks the same compiled subprogram for the same exact fraction. The second Bound still computes its own graph level and retains its own complete sample/bisection/error order. An unrelated or uncertain subprogram replays normally. Test actual Curta bank/status/stop/replay parity and measure five default production ticks with identical source and CPU affinity.

**Non-Goals:** No cross-tick/run cache, synthetic Follow Motion, algebraic reformulation of law source paths, collapsed search sample, changed `_SUBDIVISIONS`, tolerance, admission, document or author API. No viewer implementation in this Python cycle; viewer repository owns its independently measured equivalent.

## Decisions

1. Allocate a fresh prefix memo within `_reached`, shared only among constraints examined by that invocation and discarded before return. Key by the identity sequence of compiled edges and the IEEE-754 bits of the search fraction. `values`, `held` and `admissions` are the fixed arguments of this `_reached`; no persistent key for mutable state is needed. Restrict reuse to a subprogram of deterministic compiled laws ending in Follow, the measured Curta shape. A differing edge, fraction, or non-Follow subprogram uses the existing replay. This is narrower than caching a whole Run or a graph-computed Follow path; the latter may reassociate floating source arithmetic.
2. Publish only after the full original prefix edge walk succeeds. Store the resulting displacement and absolute landing mappings as private immutable snapshots; do not expose their mutable propagation object to a second consumer. The later Bound constructs its own arguments, evaluates its own graph and own value from the snapshot in the existing operation order. Its first error, one-sided closure test, original uniform fractions and bisection remain at the current call sites.
3. A cache hit skips only a proven identical successful deterministic prefix walk. A failed prefix is not cached; the next query repeats it and gets the original first error. A Bound graph failure does not invalidate a successful prefix, because that independent graph is still evaluated at each required query. Exact bit keys distinguish signed zero; nonfinite/unsupported fractions bypass reuse.
4. Keep the cache private to `_reached` rather than `Run`: no restore/reset invalidation or growth policy is needed, and a changed admission, branch, source bank, or new tick necessarily starts empty. A pair of constraints with different edge sequences never shares a replay.

## Risks / Trade-offs

- **Cached prefix hides eager error or state mutation** → scope to compiled deterministic law/Follow edges, cache only successes, evaluate each Bound graph unchanged, and test early law/Follow/Bound failures plus a changed branch and retry.
- **A near-identical fraction or cut side aliases** → key exact IEEE bits; test adjacent `nextafter` values and both one-sided outcomes.
- **Second Bound mutates a cached result** → snapshot plain mappings and let each consumer assemble fresh Bound arguments; test reversed Bound order and multiple searches.
- **Performance remains slow** → report measured gain and remaining cost honestly. This does not claim to solve all Follow partition cost or the browser runtime.

## Migration Plan

No migration. The change is internal, reversible by removing the memo path, and produces no document or persisted state. Framework and actual Curta gates precede local fast-forward integration.
