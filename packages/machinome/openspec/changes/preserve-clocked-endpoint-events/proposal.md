## Why

Enigma I's following-stroke release fails to rearm its right pawl when a clocked request ends exactly at its measured non-strict event threshold. The public empty-assembly reproduction records zero commits both at that endpoint and on continuation, while the uninterrupted request commits once, violating the existing endpoint and partition contracts.

## What Changes

- Correct clocked event admission at an exact requested endpoint without changing the authored threshold, introducing a tolerance, or adding a second locator.
- Pin the reproduced floating-point path and its partition equivalence with red-first framework regressions, retaining strict landing, tie, ordering and atomicity guarantees.
- Validate the public reproduction and real Enigma loaded-controller tests against the corrected framework.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: add explicit regression scenarios to the existing clocked request contract for the measured descending inclusive endpoint and partitioned continuation; preserve the requirement's existing semantics.

## Impact

The implementation scope is clocked request/event handling and focused tests in `machinome/simulation/clocked.py` and `tests/test_clocked_solver.py` or a focused sibling. Shared locator code changes require evidence that a clocked-only correction cannot satisfy the contract, and regressions for its existing consumers. No public API, dependency, document version, mechanical threshold or project-side locator changes are planned. Viewer/export consumers will be inspected for the same arithmetic issue; any independently necessary viewer correction belongs to its own repository and cycle.

## Authority and cycle identity

On 4 November 2026 the pilot explicitly authorized: “authorize, use sol-6.1 subagents for propose and apply, and validate empirically”, in response to the standalone framework correction and local integration scope. This is advance authorization for proposal, implementation, empirical validation and local integration, with delegated proposal/apply agent review; it is not human review of these finished artifacts. No push, publication, PR or contributor contact is authorized.

Standalone base: `b818376640e29bc51235c6b22f1962dad0fb2aa5`, clean primary branch `main`; cycle branch/worktree `preserve-clocked-endpoint-events` / `machinome/WTs/preserve-clocked-endpoint-events`; integration target is that unchanged primary `main`. The planning agent owns only planning commit 1; the apply agent owns implementation, evidence and completed commit 2.
