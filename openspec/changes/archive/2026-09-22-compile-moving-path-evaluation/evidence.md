# Curta performance and parity evidence

Originating caller: `OperatingCurta` from the independent Curta-Type-I-3x project at committed `7586002`, checked out clean and detached at `WTs/perf-758-reference`. This graph includes the higher-result-bank restraint. Its previously verified compiled-program identity is `be125f4048c8be00ce4e73d646311d4a50ac75a59aa739f93bf2f38c992fa195` (23 aggregate crank-low reads, 126,032 reachable DAG nodes; the earlier project graph had only five reads and 18,829 nodes). Runtime source SHA-256 values on the frozen worktree were:

| Source | SHA-256 |
| --- | --- |
| `simulation/running.py` | `bf32eeaf6ffd4fae3a038889af17d38616ab6a0824e8dc38b4f3c106150a825a` |
| `simulation/running_parts.py` | `9b7f755ee9c33fa12cb2b8a6b341153b454472af8c01e061a23cdb8aedeae1f8` |
| `simulation/result_bank_lockout_parts.py` | `7b6a709ea64878a7ee37df6ce454ca17a772bb7ad96d7cf1c3776f804aa67b82` |
| `simulation/higher_locking_laws.py` | `561ec3b96185b6a44f26012a3db2c9bd1013de3a868a4c9ad8af03cf7d6372c6` |
| `simulation/higher_locking_profiles.py` | `1cf2bed3b1be41ba66bccc2eb788fb24ddc5c21698853478e8d0f02813e10529` |
| `simulation/counter_locking_laws.py` | `0c1a5fba52ff428abf0188c9016a21efef90271882fd311fd5d8e62fdbb39bac` |
| `simulation/counter_locking_profiles.py` | `eaa3bd7dfbdb58e20a32549a748e11745737b8d2598d4d37ff7496c46ce4f367` |

Reproduction in both runs: `Sim(OperatingCurta(), dt=.1)`; three completed zero-duration preparations `digit_3 → 3`, `crank_rotation → 160`, `digit_3 → 0`; command `move('crank_rotation', to=170, duration=.1)` followed by `run(.1)`. Both Python processes used the workspace venv, `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `SOLID_BUILD_DIR=_build_checks`, and `taskset -c 14`; `PYTHONPATH` selected either framework main at `6dc07a8` or this uncommitted candidate worktree, always followed by the same frozen project worktree. The parent constrained its long-running arithmetic and geometry jobs to CPUs 0–11 during this pair. Other user processes were not controlled. Times below are unprofiled `time.process_time()` with wall time measured separately; one sequential A/B pair, not a statistical distribution.

| Framework | Preparation CPU / wall (s) | Active stop tick CPU / wall (s) | Outcome |
| --- | ---: | ---: | --- |
| Main `6dc07a8` | 29.302 / 29.808 | 8.620 / 8.626 | Blocked at `165.22323837279146` |
| Candidate `aea1340` plus path diff | 28.124 / 28.602 | 7.885 / 7.887 | Blocked at `165.22323837279146` |

The candidate saves **0.735 CPU s (8.52%)** on this active searched-stop tick. Both banks have 213 entries and the same canonical JSON SHA-256 `f5c67383a964a55ded731637e8612efffd1938725f7ec0417fc85d6e4cb6f1a9`; all three preparation commands completed. This is a bounded improvement, not a claim that an ordinary Curta turn has become interactive. No search sample, tolerance, dt, law, or mechanical part changed.

Red-first: `tests.test_compiled_path_evaluation` failed at the repeated-sample node-hash assertion against `6dc07a8` before implementation. After implementation, its five tests and eight adjacent expression/path tests passed, including an additional at-time missing-input/arithmetic-error precedence guard suggested by independent review. Broader running-path/read/stop, clocked-bound/solver/corpus, and expression graph tests passed (238 tests). Running carry timing, corpus, jumps, play, selection, time drive, source-timing document, and simulation tests passed (259 tests). All 34 strict baseline specs and the strict change validation passed. An independent read-only review of the bind/at diff by the framework reconciliation agent found no semantic regression: node/operand order, eager errors, standing refresh, failed-bind publication, min/max fallback, and graph lifetime were checked.
