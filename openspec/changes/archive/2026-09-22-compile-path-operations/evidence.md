# Curta path-operation evidence

Originating caller: independent Curta-Type-I-3x project, clean detached `WTs/perf-758-reference` at commit `7586002`, compiled-program identity `be125f4048c8be00ce4e73d646311d4a50ac75a59aa739f93bf2f38c992fa195`. This is the expanded 23-read crank-low graph with the physical higher-result-bank restraint. Framework baseline was main `3afb3f7bab4bbb60530db62a035e5a71e37ce931`; candidate was planning commit `e96b5ca` plus the uncommitted implementation in this isolated worktree. The later primary-project geometry edits were not included.

All measured Python processes used the workspace venv, `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `SOLID_BUILD_DIR=_build_checks`, CPU affinity `taskset -c 14`, and `PYTHONPATH` selecting baseline or candidate framework followed by the same frozen project. The parent kept its long mechanical jobs on CPUs 0–11; other user processes were not controlled. Times are `time.process_time()` and monotonic wall time, one sequential A/B pair rather than a statistical distribution.

The ordinary operation was `Sim(OperatingCurta(), dt=.1)`, zero-duration `digit_1 → 1`, then `crank_rotation by 360 duration 2`, followed by twenty `.run(.1)` ticks. Both completed at exactly 360° with result-bank reading 1. The complete 213-coordinate final state was bit-identical via canonical JSON SHA-256 `f410f00096a075fef933ffbc5e5490c05046720dc942c615a3e6cab94b8b98a7`.

| Framework | Init CPU / wall (s) | Whole turn CPU / wall (s) | Ordinary 162→180° tick CPU (separate process) |
| --- | ---: | ---: | ---: |
| Baseline `3afb3f7` | 4.255 / 4.908 | 72.564 / 72.859 | 3.404 |
| Candidate callable path program | 4.085 / 4.739 | 59.112 / 59.170 | 2.890 |

The whole ordinary turn saved **13.452 CPU seconds (18.54%)**, and the separate midpoint pair saved 0.515 CPU seconds (15.1%). This is a material cost reduction, but 59 seconds for two simulated seconds is not interactive.

An instrumented pair captured each searched Bound's existing ordered samples, not just the endpoint: the first tick had 130 bound/replay evaluations and exact SHA-256 `790237a83daddb0c11422f03cb001142f8895e059898754b0503afba84dc7778` in both versions. The first ten ticks had 1,300 ordered evaluations and exact SHA-256 `402ff5bf0dd6a216e19bfbf180630af1729d28309a3cf94b54def24bc21a6aa7` in both; their 213-coordinate state was exact SHA-256 `3d2ea5b2bb0fc7bbc408ea1bcf144c1e278624e463fd069284a9722908c5e370`. Captured entries included each constraint identity/side, sample input float hex values and bound result float hex values for traced paths, or sample fraction and level float hex for the replayed pawl Bound. The temporary probe was removed before the implementation commit.

The red-first operation-classification test failed against baseline at `node.kind` reread in `_PathValue.at`. After implementation, 10 focused tests passed; 322 broader expression, running-path, jump, stop, carry-timing, play, selection and corpus tests passed. All 35 strict OpenSpec items, including this change, passed. An independent read-only reviewer found no semantic blocker after checking eager bind and first-error order, float/unary/extremum calls, current standing values, path lifetime and malformed arity. The reviewer noted that monkeypatching private math/operator tables **after** binding no longer changes this path's later calls; that is not part of the immutable compiled-law public contract.

No source-timing, constraint sample count, tolerance, dt, authored law, mechanical part, viewer format or document field changed.
