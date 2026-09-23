## ADDED Requirements

### Requirement: An unobstructed absolute running request lands at its exact native target

For `move(input, {to, duration})`, the viewer SHALL retain the converted native target independently of the requested travel. When the request's full last admission is unobstructed, the input and every determined closed-numeric endpoint used by the stop judgment SHALL be evaluated and committed consistently with that target, even when `start + (target - start)` rounds to a different binary64 value. An uncertain or declared stateful descendant expression SHALL retain its existing evaluation count, order and arithmetic rather than being re-evaluated solely for endpoint correction; the input itself still lands at the requested target. This closed-numeric guarantee assumes the normal viewer platform with standard Math functions. Reaching an inclusive declared bound exactly SHALL complete without a stop record. The viewer SHALL retain existing intermediate path, per-tick cadence, bounds, search samples and actual outward-stop behavior; it SHALL NOT grant an endpoint correction to a clipped or blocked partial admission.

#### Scenario: Curta-derived one-ULP upper endpoint
- **WHEN** a feed starts at `-4.942499999999999` and a direct driven carriage with upper bound `3.9075` receives `move(feed, {to: 3.9075})`
- **THEN** the command completes, feed and carriage equal `3.9075`, and no upper stop is recorded

#### Scenario: Exact first endpoint changes the next subtraction
- **WHEN** the preceding absolute request asks for `to=-4.9425` and the following request asks for `to=3.9075`
- **THEN** each unobstructed input endpoint is exactly its own target, even if fixing the first endpoint changes the second request's rounded delta and the final bound decision

#### Scenario: Genuine outward request still stops
- **WHEN** the same feed receives a target strictly beyond the carriage's upper bound
- **THEN** the existing search locates a physical stop, reports blocked with admitted travel, and commits no outside bank

#### Scenario: Intermediate path and partial stop retain their meaning
- **WHEN** an absolute request spans several ticks or meets a bound before its final endpoint
- **THEN** every intermediate tick and partial stop uses the original admissions and search fractions, with no early target snap

#### Scenario: A stateful descendant retains its evaluation cadence
- **WHEN** a determined law reads `random()` directly or through a binding alias on an exact-target tick
- **THEN** the input lands at the target, while the law's call count and result follow the existing path without an extra terminal read or a forced prefix replay

### Requirement: Absolute targets remain exact through snapshot replay

An active `move(to)` command SHALL retain enough endpoint information through snapshot and restore to reproduce its final native target, command status, complete bank and stop record. A restore record with a present malformed, wrong-type or nonfinite native target SHALL refuse before replacing the running state; an older record without this optional field SHALL retain the prior reconstruction behavior. Relative `move(by)` and rate commands SHALL retain their existing arithmetic and observable results. No new host operation or document version is introduced.

#### Scenario: Restore before the final tick
- **WHEN** a multi-tick absolute request is snapshotted before its final tick, restored and replayed
- **THEN** the final endpoint and full bank equal the uninterrupted run and the command has the same outcome

#### Scenario: Relative movement is unchanged
- **WHEN** the same starting bank receives `move(by)` rather than `move(to)`
- **THEN** it follows the existing relative-travel arithmetic and the existing physical-stop decision

#### Scenario: Malformed active target refuses atomically
- **WHEN** a snapshot record carries a present native target of the wrong type or a nonfinite number
- **THEN** restore refuses it and leaves the current bank, tick and active commands unchanged
