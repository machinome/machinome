# Completion evidence

Framework base `471d00ae5da86e2e86e0e4ff1824c8f734ea9e78`; originating Curta project clean tracked checkpoint `f7e4945`. The project source hashes below were unchanged across the paired benchmark:

- `simulation/running.py` `588ff2a3e59931a6a002106648f82c6ab7f9055b2565e7e24d4bd9bafc5ad385`
- `simulation/running_parts.py` `04c0cf2781de4e7b4cf792e1f25d045c35779b20f59f8b4c073e1501fdf525fc`
- `simulation/counter_locking_laws.py` `0c1a5fba52ff428abf0188c9016a21efef90271882fd311fd5d8e62fdbb39bac`
- `simulation/counter_locking_profiles.py` `eaa3bd7dfbdb58e20a32549a748e11745737b8d2598d4d37ff7496c46ce4f367`
- `simulation/higher_locking_laws.py` `561ec3b96185b6a44f26012a3db2c9bd1013de3a868a4c9ad8af03cf7d6372c6`
- `simulation/higher_locking_profiles.py` `1cf2bed3b1be41ba66bccc2eb788fb24ddc5c21698853478e8d0f02813e10529`

The new test failed first because a numeric path `min/max` entered the generic `_face` dispatcher once. After direct dispatch to the same Python built-ins used by the numeric face, it passed exact-float bit comparisons against `GraphValue` across operand order, signed zeros, NaN and changing values, plus unresolved-input recovery. This preserves every visited graph node and every chart term.

Mesh-free `OperatingCurta`: construct `Sim(..., dt=.1)`, select `digit_1=3`, then move the crank 18° over 0.1 simulated seconds. Process CPU for that tick fell from 4.321 to 3.496 seconds (19.1%); all 213 state entries retained exactly the same JSON-sorted SHA-256 digest `ae326e24781efb54bd2914a1823805d470c20f1898835470b0168055eb4647aa`. This is a bounded tick, not a claim about every operation. Expression, source-timing, carry, stop, read, selection and exact-geometry regressions passed: 341 tests. No search count, tolerance, dt, public math function, viewer document or CAD geometry changed.

No ADR is warranted: the optimization is a private numeric call choice inside an existing evaluator, not a new architectural dependency or public interface. The pilot's clean-worktree exception preserves primary's pre-existing untracked `docs/examples/v8-engine/` unchanged.
