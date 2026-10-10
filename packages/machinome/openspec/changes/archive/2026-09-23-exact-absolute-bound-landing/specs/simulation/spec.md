## ADDED Requirements

### Requirement: An absolute move preserves its stated terminal coordinate

For `move(input, to=target, duration=...)`, the running simulation SHALL preserve the once-converted native target independently of the travel `target - current`. At the full terminal admission, the input SHALL stand at that exact native target, including its signed-zero bit, and its determined coordinates and numeric Bounds SHALL see the corresponding terminal endpoint before stop detection and commit. An exact endpoint on an inclusive bound SHALL complete without a stop. This SHALL hold for zero- and positive-duration moves, after snapshot/restore, and in both rounding directions, without changing the motion at earlier fractions or the semantics of `move(by=...)` and `rate(...)`. A current snapshot of an active absolute move SHALL retain the target separately and restore SHALL validate its numeric finite form atomically; a legacy snapshot without this added internal field SHALL not be guessed into a different target. A request that genuinely travels beyond a bound SHALL still stop and report its actually admitted travel; the system SHALL not relabel a blocked result after committing an overshoot or introduce a clearance tolerance.

#### Scenario: A rounded travel does not turn an exact upper landing into a stop
- **WHEN** a driver at the binary64 value immediately above `-4.9425` drives a Prismatic joint whose inclusive upper bound is `3.9075`, and `move(to=3.9075)` is requested
- **THEN** both input and directly determined joint end at exactly `3.9075`, the handle reports `completed`, and no upper stop is recorded, even though adding the rounded travel to the starting value would have produced `3.9075000000000006`

#### Scenario: A read-dependent bound agrees at its endpoint
- **WHEN** the same move meets an upper `Bound` reading a standing coordinate at `3.9075`
- **THEN** the bound's terminal sample sees the exact target and the move completes without changing the existing interior samples or search rule

#### Scenario: An actual crossing is not hidden
- **WHEN** the same mechanism requests a target strictly beyond the stated upper bound
- **THEN** it reports `blocked`, commits at the physical stop under the existing rule and does not silently land the requested endpoint

#### Scenario: Timed target survives restore
- **WHEN** a positive-duration absolute move is snapshotted before its final tick and replayed after restore
- **THEN** both runs admit the same intermediate travel and finish with the same exact target, status, bank and stop records

#### Scenario: A malformed saved target cannot partly restore
- **WHEN** a snapshot's optional active absolute target is a nonnumeric value or a nonfinite float
- **THEN** restore refuses it before changing the current run, while a legacy snapshot without that optional field retains its old record interpretation without inventing an endpoint

#### Scenario: Relative and signed-zero semantics remain distinct
- **WHEN** an otherwise identical `move(by=...)` is issued, or an absolute target is negative zero
- **THEN** the relative request retains additive travel semantics, while the absolute request retains the requested native endpoint bit on completion
