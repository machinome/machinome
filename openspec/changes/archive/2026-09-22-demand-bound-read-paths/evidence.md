# Bound-read path demand evidence

Originating caller: independent Curta-Type-I-3x project, clean detached
`WTs/perf-758-reference` at commit `7586002`. Its compiled program identity is
`be125f4048c8be00ce4e73d646311d4a50ac75a59aa739f93bf2f38c992fa195`.
The physical `reverse_stop` reads a retained own-read anti-reversal pawl
coordinate named by no later edge. On framework baseline `acebc48`,
`Program.deltas_of` does not demand that coordinate, so its Bound replays a
four-edge prefix at the existing 65 search fractions on each ordinary tick.

The test fixture in `tests/test_bound_read_demand.py` reproduces that shape
with a real running program. Before the implementation it failed because the
Bound-only retained coordinate was absent from `Propagation.demanded`. After
the change, the coordinate is demanded and the Bound uses its actual path
without a prefix replay. A separate inactive Bound with equal endpoint values
and an interior singularity completes both an idle tick and a moving-source
tick without evaluating the unused interior. That latter test also passes on
the unchanged `acebc48` baseline. Existing Play/untraced prefix-replay tests
remain green.

The real Curta ordinary operation was `Sim(OperatingCurta(), dt=.1)`, a
zero-duration `digit_1 → 1`, then `crank_rotation by 360 duration 2` over
twenty `.run(.1)` ticks. Both baseline and candidate completed at exactly
360° with 213 bank coordinates and identical JSON/SHA-256 state
`3fbe9e81590c63ab8ed5c3f2bb0dbede1cff07acd9235c1598bdb70cc4e27031`.
An instrumented candidate captured all 2,600 existing ordered Bound level
returns `(identifier, side, fraction.hex(), level.hex())`; SHA-256 was
`4e9397b1ccdb614987bef2d1947a0e5e9b68d2cdcf4aa9768e2b9776fecd46de`,
identical to the earlier process-local baseline capture on the same `acebc48`
and frozen project. No search fractions, bisections, tolerances, dt, laws or
Bound argument rules changed.

For the stopped withdrawal, setup was `digit_3 → 3`, `crank_rotation → 160`,
`digit_3 → 0` at zero duration, then a 160→170° request over 0.1 s. Baseline
and candidate blocked at exactly `165.22323837279146` with admitted
`5.223238372791457`, identical 213-state SHA-256
`75e32df30c33a0bdea563a29d40e901d21423862182ce8d4920ac2ac4240644b`
and identical 134 ordered searched-level returns SHA-256
`2db39d3bff6cdc3fb8194cfd003221a99886332e8c582ebeed821ef8bbcda95a`.

The paired uninstrumented ordinary-turn run used the same workspace venv and
frozen project with `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`,
`SOLID_BUILD_DIR=_build_checks`, and CPU affinity `taskset -c 14` for both
processes. Root's separate long mechanical jobs occupied CPUs 0–11; other
user processes were not controlled. Baseline `acebc48` took **55.933 process
CPU seconds** for the turn; candidate took **24.770**, a **55.7% reduction**.
This is a single sequential pair, not a distribution, and is not yet an
interactive browser claim. Instrumented stopped-tick CPU was 12.093→10.242 s;
profiling overhead makes those numbers unsuitable as ordinary runtime estimates.

The focused running/path/Play/stop set passed 141 tests. The broader relevant
running, source-timing, expression, constraint, control and simulation set
passed 827 tests. `openspec validate --all --strict` passed 35/35 items.
A repository-wide `unittest discover` run covered 3,626 tests but did **not**
pass: 53 errors included geometry build-file/lock `FileNotFoundError` under
`tests/_build` (for example a meta-project STL lock path); its enormous output
was truncated, so the 53 errors are not classified as all environment-only.
The green 827-test relevant gate, exact real caller parity and independent
read-only review are the acceptance evidence for this scoped change; the
repository-wide failure remains an explicit validation limit.

This only changes a private compiled program's propagation demand. ADR-137's
path semantics and replay fallback already cover the decision; no new ADR or
architecture synthesis change is warranted. The program identity, published
document and source-timing contract remain unchanged.
