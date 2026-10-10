# Completion evidence

Framework base `9f693bb9c55ff8967e427dbdac9e97de5f9d7fee`; Curta project HEAD `1f807fb` with these unchanged source hashes throughout the paired test:

- `simulation/running.py`: `588ff2a3e59931a6a002106648f82c6ab7f9055b2565e7e24d4bd9bafc5ad385`
- `simulation/running_parts.py`: `f732d76439c82cd4c659b8fb9a56fa291f95baa4433565df0c60a00fb0ec17a8`
- `simulation/counter_lockout_parts.py`: `f6a5d7184354ef715069e82e5c1efb9f646a74a8d04763f7ec23a129b2319cda`

The pilot explicitly allowed a clean isolated framework worktree while preserving primary's pre-existing untracked `docs/examples/v8-engine/`; those files were not moved or edited. The added test was red first: repeated successful `bind` calls traversed the graph twice instead of once. It also covered changing input values, failed-first-bind recovery, later path samples and graph reclamation. The implementation makes both tests green by caching only a path-local immutable node order after the first successful bind.

For the mesh-free OperatingCurta operation `Sim(OperatingCurta(), dt=.1)`, `digit_1=3`, and one 18° crank move over 0.1 simulated seconds, process CPU for the crank tick fell from 5.952 to 5.323 seconds (10.6%). The full 213-entry state retained exactly the same SHA-256 digest `ee8d6f04adcab85a32bf0920951aa375412860c8bd259e52079a06c7540105e2`. This is one bounded tick, not a whole-operation speed claim.

Expression, expression-sharing, corpus, binding, source-timing, carry, stop, read and selection regression suites passed: 277 tests. The cache does not change 64-sample constraint search, tolerances, time steps, arithmetic operators, error order or input values. No ADR is needed: it introduces no public interface or new architectural dependency.
