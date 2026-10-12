## ADDED Requirements

### Requirement: A clean path rebind allocates no change-tracking state

When successive pieces present the same input values and presence to a followed expression, the viewer SHALL reuse its retained graph values without allocating a dirty-node set or replacement input snapshots. Input observation order, first-error behavior, changed-input propagation and resulting floats SHALL remain identical to a whole bind; no search point, admission, committed coordinate or replay may change.

#### Scenario: Distinct equal bank objects
- **WHEN** a followed path is rebound with a distinct values object containing the same relevant keys and values
- **THEN** no expression node is recomputed and no change-tracking state is allocated

#### Scenario: Changed input after clean pieces
- **WHEN** a later rebind changes a relevant value or key presence
- **THEN** it propagates exactly the changed node cone and returns the same bits as a whole bind

#### Scenario: IEEE values and error timing
- **WHEN** inputs include signed zero or NaN, or a later input access throws after an earlier input changed
- **THEN** the same change classification and first thrown error occur in the same input order

#### Scenario: OperatingCurta default-tick crank window
- **WHEN** the pinned 213-coordinate OperatingCurta export runs the first 48 ticks of a declared two-second turn at default dt
- **THEN** its search samples, admission and committed coordinate bank match the baseline while process CPU falls materially on the same host
