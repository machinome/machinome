# Evidence: tick-local folded law graphs

Origin: Curta Type I `simulation.running.OperatingCurta`, unchanged project source. Framework base `23857e9227c85efb8a99d0f1d1951ee5b62ab0ec`; isolated cycle worktree `machinome/WTs/cache-folded-law-graphs`. Command for the production comparison: `Sim(OperatingCurta(), dt=.1)`, move `crank_rotation` to 90 in `.5`, then run `.5`, pinned to CPU 12 and using the same `_build_checks` directory. No document, sample, tolerance, or project graph changed.

Before implementation, a read-only diagnostic counted 7,240 `_folded` calls and 1,862 distinct root/full-substitution states in this five-tick command (5,378 repeats). An experimental 256-entry per-tick memo showed 19.744→16.540 process CPU seconds with the same bank. The implementation is narrower: exact built-in finite numeric inputs and tick-local lifetime.

Red first: six new focused cases failed because `_folded_tick_cache` was absent on the unchanged base. The completed test includes a counted uncached fold proving one structural walk for two identical successful calls; failed eligible folds never publish. The nine focused controls cover signed-zero distinctness, root and full-mapping identity, custom conversion, NaN/infinity, overflowing unused built-in integer, eviction, nested scopes, failed tick cleanup, and separate runs.

Production baseline/candidate, same command and serialization:

| Proof | Baseline | Candidate |
| --- | ---: | ---: |
| CPU 12 process seconds, with Bound-level tracing | 22.403 | 19.518 |
| Ordered prefix Bound levels | 768; SHA-256 `72dc67addbc780a6d9f3d5cb92c65ffcde52798f9f31b3e149d9c29718179a0c` | identical |
| Full 214-coordinate bank | SHA-256 `8707183ffb160d3050f6680dc65d4198f01666c14f7aba8865a58d8f2f1092a7` | identical |
| CPU 12 process seconds, repeat without trace | 22.717 | 19.793 |

The ordered trace hashes `repr` of `(constraint id, side, IEEE-hex fraction, IEEE-hex level)` for every `_constraint_level` call. The bank digest hashes `repr(sorted(sim._run.bank.items()))`. It is intentionally not compared to another agent's digest made with different command/serialization. Improvement is ~12.9% in these paired process-CPU runs, not a universal speed claim.

On the candidate, the same project command run after `sim.restore(rest_snapshot)` yielded `sim.snapshot() == reached_snapshot` and the same full-bank SHA-256 before and after replay. This demonstrates this cache's one-tick lifetime across a real restore/replay, in addition to focused scope-reset tests.

Framework gate before the final test-only boundary additions: `3613 passed, 4 skipped, 2131 subtests` in 405.27 s. Final focused cache and Follow suite: `28 passed` in 2.06 s. No viewer consumer or wire change exists. No new ADR is warranted: this is private bounded reuse under existing running-path architecture, with no new product decision or public contract.
