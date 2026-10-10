## 1. Red proof and baseline

- [x] 1.1 Add a red test for repeated path traversal, changing piece inputs, first-bind error recovery and graph release.
- [x] 1.2 Record current Curta source hashes, exact bank and CPU for one bounded crank tick.

## 2. Implement and verify

- [x] 2.1 Reuse each path's graph order after its first successful bind and make focused tests green.
- [x] 2.2 Recheck the same Curta source hashes and exact bank, measure CPU, and run expression/source-timing/carry/stop regressions.
- [x] 2.3 Sync the expression-sharing spec, archive, validate and integrate the two-commit cycle.
