## 1. Red evidence and declarations

- [ ] 1.1 Add a mesh-free framework fixture reproducing the Vault checkpoint `78d4ceb` path and independent scalar play oracle; prove pickup, reversal, cadence, and three-wheel cascade tests red before implementation.
- [ ] 1.2 Add red declaration/refusal tests for the public `Play` export, finite ordered offsets, exact relation shape, running-only banked target, invalid initial interval, and unsupported source graphs.
- [ ] 1.3 Add red adversarial tests for exact and non-integer flanks in both directions, multiple-turn/large travel, long versus split requests, downstream reads, snapshot/restore/reset, and atomic refusal.

## 2. Play declaration and compilation

- [ ] 2.1 Implement the immutable lazy-exported `Play(low, high)` law marker and integrate its exact source/retained/driven shape with relation realization without changing callable laws.
- [ ] 2.2 Compile dedicated play edges, validate initial admissibility, and admit only linear chains rooted at a run-owned driver; refuse cycles, ambiguous writers, and arbitrary potentially reversing sources by relation identity.
- [ ] 2.3 Include play kind, endpoints, and offsets in program descriptions and identity while keeping programs without play byte-identical.

## 3. Running behavior and stops

- [ ] 3.1 Apply the endpoint projection in program order using only the ordinary bank, with exact retention, either-flank pickup, and immediate reversal release.
- [ ] 3.2 Locate bounded play-chain followers by replaying the complete prefix from the originating driver; prove the two-gap `x=40, y=30, z=20` counterexample and release-side freedom.
- [ ] 3.3 Preserve tick rollback, command statuses, records, tree pose, reset, snapshot, and restore invariants across play propagation and stop refusal.
- [ ] 3.4 Run the unchanged originating Vault callable prototype as a regression control and record its existing pass/failure evidence; separately migrate a representative Vault caller to Play, rooted directly at the dial driver, and prove the existing mechanical acceptance assertions pass. Do not change callable-law semantics to turn the old prototype green.

## 4. Publication and parity contract

- [ ] 4.1 Publish explicit `kind: "play"` edges with ordered `needs`, `gives`, `low`, and `high`, and select document version 9 only when one is present.
- [ ] 4.2 Add viewer-version refusal tests proving a versions-1-through-8 consumer cannot silently execute a play document.
- [ ] 4.3 Extend and regenerate the running conformance corpus with every required play behavior and coverage refusal, while proving prior committed documents and the no-play corpus content remain unchanged.

## 5. Documentation and completion evidence

- [ ] 5.1 Document `Play` as a narrow running backlash/clearance mechanism with its formula, admitted source restriction, invalid-rest refusal, and Vault example; state that browser execution awaits independent viewer version-9 support.
- [ ] 5.2 Run focused play, running self-read, stop, document, corpus, and API tests plus the full framework suite; retain the existing 42-test/62-subtest self-read control and report environmental failures honestly.
- [ ] 5.3 After implementation evidence settles the design, record the architecture decision if consequential, update `docs/architecture.md` and ADR index as applicable, synchronize baseline specs, validate, and archive the change under the framework cycle protocol.
