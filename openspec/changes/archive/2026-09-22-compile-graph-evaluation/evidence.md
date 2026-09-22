# Completion evidence

Framework base `70d0bd9`; originating Curta project tracked checkpoint `7586002`. Current `OperatingCurta` compiled program identity was `be125f4048c8be00ce4e73d646311d4a50ac75a59aa739f93bf2f38c992fa195` on both framework versions. The current crank-low aggregate reads 23 coordinates and contains 126,032 reachable DAG nodes; frozen project checkpoint `f7e4945` had identity `ae6a7f69b3fae2cc47f2fd3df0baf1aff14a297d06526855a3e52043a27221eb`, 5 reads and 18,829 nodes. Both have 13 constraint-table entries and 228 edges because the additional `Bound` merges into the crank-low aggregate. The comparison used a temporary clean detached project worktree, removed afterward; no project source was edited.

Current runtime source hashes were unchanged across the paired benchmark:

- `simulation/running.py` `bf32eeaf6ffd4fae3a038889af17d38616ab6a0824e8dc38b4f3c106150a825a`
- `simulation/running_parts.py` `9b7f755ee9c33fa12cb2b8a6b341153b454472af8c01e061a23cdb8aedeae1f8`
- `simulation/result_bank_lockout_parts.py` `7b6a709ea64878a7ee37df6ce454ca17a772bb7ad96d7cf1c3776f804aa67b82`
- `simulation/higher_locking_laws.py` `561ec3b96185b6a44f26012a3db2c9bd1013de3a868a4c9ad8af03cf7d6372c6`
- `simulation/higher_locking_profiles.py` `1cf2bed3b1be41ba66bccc2eb788fb24ddc5c21698853478e8d0f02813e10529`
- `simulation/counter_locking_laws.py` `0c1a5fba52ff428abf0188c9016a21efef90271882fd311fd5d8e62fdbb39bac`
- `simulation/counter_locking_profiles.py` `eaa3bd7dfbdb58e20a32549a748e11745737b8d2598d4d37ff7496c46ce4f367`

Red-first tests showed repeated `GraphValue.evaluate` hashing nodes again and entering generic numeric `min/max` face dispatch. A reviewer then exposed a malformed-arity regression shared by the new full-graph fast path and the prior motion-path fast path: Python built-ins have different arity behavior from the public two-argument functions. A separate red test proved the exact TypeError mismatch for 0, 1 and 3 operands; both evaluators now delegate only malformed arities to the original functions at the original evaluation node. The reviewer rechecked the repaired implementation and found no further semantic divergence. Tests cover shared nodes, changing inputs, exact signed-zero/NaN bits, prior missing-input and arithmetic errors, invalid operation timing, arity messages and graph collection.

For mesh-free `Sim(OperatingCurta(), dt=.1)`, `digit_1=3`, then one 18° crank move over 0.1 simulated seconds, process CPU fell from 6.876 to 5.920 seconds (13.9%). All 213 state entries retained exact JSON-sorted SHA-256 digest `ae326e24781efb54bd2914a1823805d470c20f1898835470b0168055eb4647aa`. This early 0–18° tick takes a held-read fast path for the new bank bound, so it does not claim active-sector or full-turn speed. Profile before implementation: 41,029 `GraphValue.evaluate` calls/9.49 profiled seconds, 1.69 million generic `_face` classifications; `_PathValue.at` 186,008/5.45 seconds, `bind` 74,048/1.32 seconds. No chart terms, source timing, dt, tolerances or search samples were removed.

Expression, source-timing, carry, stop, read, selection and exact-geometry regressions: 346 tests passed. No ADR is needed: the positional plan remains local to one existing value and creates no public interface, process-wide registry or dependency. The pilot's clean-worktree exception preserved primary's pre-existing untracked `docs/examples/v8-engine/` unchanged.
