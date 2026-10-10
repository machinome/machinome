# ADR-139: A Running Bound Reuses Proven Standing Bind Values

**Status:** Accepted

**Date:** 2026-09-22

**Amends:** [ADR-124](ADR-124-only-what-moves-along-a-tick-s-path-is-evaluated.md)'s no-cross-tick-cache decision, only for a running constraint's first-point standing subgraph. All other path values remain path-local.

**Preserves:** ADR-113's bound-path search and first contact, ADR-137's determined read paths and prefix-replay fallback, the complete evaluator's arithmetic and error order.

**OpenSpec change:** [cache-standing-bound-bind](../../../openspec/changes/archive/2026-09-22-cache-standing-bound-bind/)

**Extended 2026-09-22:** [ADR-140](ADR-140-a-path-reuses-only-its-own-identical-successful-bind.md) separately permits an identical successful rebind on one existing path object. Its path-local lifetime is not this ADR's Run-owned Bound snapshot.

## Context

ADR-124 made a path value local to one path. At that time cross-tick structure reuse saved only 5% and introduced stale-cache questions. `OperatingCurta` now has a different measured burden: at the viewer's default `dt=1/240`, its crank's lower Bound eagerly binds 126,032 expression nodes each tick, yet just 1,479 depend on the moving bell. On the frozen production program `be125f4048c8be00ce4e73d646311d4a50ac75a59aa739f93bf2f38c992fa195`, the first 47 tick transitions changed only bell turn and the bound's held own argument; the latter is not even referenced by the graph. The 124,553 standing nodes consequently reevaluate the same finite operands at every first sample.

The old first-eight-tick search consumed 1.722 CPU seconds binding the complete graph and 0.199 seconds evaluating all 512 later samples. A cache of samples or a smaller `_SUBDIVISIONS` would change contact semantics. Reusing a *successful standing bind* can avoid the dominant work without changing any sample.

## Decision

The `Run` owns at most one successful standing-bind snapshot per compiled constraint. A new `_PathValue` remains local to each traced search. At its existing first sample, it may reuse the previous graph's standing values and positional moving program only when the graph root is identical, the moving-name set is identical, and every graph-referenced standing input in the actual first-sample arguments is a builtin finite numeric value with exactly identical IEEE-754 bits. This includes the sign of zero. Unreferenced passed arguments do not invalidate the proof. Missing, nonnumeric, custom-converting, NaN and infinite values, a different moving shape, or a different graph take the original eager full bind. An undetermined path retains prefix replay; an inactive bound is never evaluated.

On a hit, the moving nodes are evaluated at the new first point in their original postorder with the original selected numeric operators. The fresh path becomes visible only after that evaluation succeeds. A failed full bind or hit never seeds or replaces the snapshot; a successful full bind or hit supplies the next single entry. Every later sample follows the unchanged moving program. Successful restore/reset clears the run's entries; a new run starts empty. No cache is process-global or outlives its owner.

The original full evaluator can only have seeded a snapshot after its whole postorder succeeded. With identical immutable graph and finite standing operands, its standing arithmetic cannot acquire a new error or different float. A changed standing input takes the original walk, preserving its earliest error even when a later moving expression also fails. Run-produced first-sample arguments are numeric; cache validation declines arbitrary `__float__` objects rather than invoking a conversion out of order. The compiled numeric vocabulary is closed to pure degree-math functions and operators; unlike the viewer's independent JavaScript context, it has no `random` or time opcode. Dynamically monkeypatching numeric operator implementations during a live run is outside the compiled-law contract.

## Alternatives

- **Keep all path values path-local.** Safe and still used elsewhere, but now costs over 20% of the actual first-48-tick Curta run in redundant standing arithmetic.
- **Cache by object identity, source object identity, or `==`.** Rejected: mutable placeholders and source objects change value without changing identity, and Python equality merges opposite signed zeros and mishandles NaNs.
- **Cache the entire bound result or contact search.** Rejected: moving nodes and fixed search samples must still run, including their errors and first-contact behavior.
- **One cache per process or an unbounded history of input tuples.** Rejected: graph lifetime and memory would outlive the run, and no originating project needs it.
- **Cache all `_PathValue` users.** Rejected: the project evidence concerns the first bind of traced running Bounds; jumps and law paths retain ADR-124's path-local behavior.

## Consequences and Evidence

There is no new declaration, public API, tolerance, timestep, sample count, or document field. On frozen Curta commit `7586002`, first 48 default-dt ticks fell from 44.501 to 33.246 process CPU seconds (25.3%); the current production program fell from 51.976 to 34.875 seconds (32.9%). Complete 360° project-style turns at `dt=.1` saved 19.5% and 17.6%. The stop/replay path was numerically exact but not materially faster. Both programs retained exact 213-coordinate banks and bit-identical ordered bound argument/result traces: 6,240 first-48 evaluations, 2,600 full-turn evaluations and 398 active-stop/replay evaluations each. The originating project, identities, commands and hashes are recorded in the archived change's `evidence.md`.

The extra state is one immutable positional snapshot per compiled constraint on the owning run, plus finite input bits. The cache can miss often without changing behavior. It does not make the full Curta interactive by itself: propagation and eager evaluation of changed or newly bound graphs remain substantial costs. A separate viewer cycle must justify and prove its own cache against JavaScript's evaluator, including its `Math.random` context; this decision does not apply viewer semantics to Python.
