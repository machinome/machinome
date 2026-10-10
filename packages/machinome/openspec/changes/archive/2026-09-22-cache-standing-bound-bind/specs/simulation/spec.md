## ADDED Requirements

### Requirement: An unchanged standing constraint subgraph is not rebound on every running tick

For a sampled running constraint whose determined path is available, the run SHALL evaluate the bound at the same first point and every subsequent search point, in the same order and with the same operators and values as a complete expression walk. After one successful first-point evaluation, the run SHALL reuse the standing nodes of that bound on a later search only when the compiled graph and moving names are the same and every graph-referenced standing input has the same finite IEEE-754 value, including its sign bit. It SHALL evaluate moving nodes at the later search's first point and every required later point. If equality or safety cannot be proved, the original complete first-point evaluation SHALL occur. This reuse SHALL change no search fraction, crossing, stop, refusal, bank value, error order, document, or author declaration.

#### Scenario: Unchanged standing inputs on successive Curta crank ticks

- **WHEN** the Curta's crank constraint is searched on successive ordinary ticks while its bell turns and its other graph-referenced inputs stand at identical finite values
- **THEN** the standing portion is not numerically reevaluated at every first point, the moving portion is evaluated at the same first point and all fixed search points, and the complete coordinate bank and ordered constraint levels equal a full-bind run bit for bit

#### Scenario: A standing input changes or a branch shape changes

- **WHEN** a later search changes any graph-referenced standing input or its moving-name set
- **THEN** that search uses the complete first-point bind, preserves the first error and all later samples, and a successful bind may become the new bounded reuse entry

#### Scenario: Equality cannot establish safe numeric identity

- **WHEN** a referenced standing input is missing, nonnumeric, NaN, infinite, or differs only by the sign of zero
- **THEN** the run does not reuse the earlier standing values and observes the same value or first error as a complete bind

#### Scenario: A failed bind and a quiet or untraced search

- **WHEN** a first-point bind fails, a bound is inactive, or a determined path is unavailable and the existing prefix replay is required
- **THEN** no successful standing cache is inferred from the failure, the inactive bound remains unevaluated, and the prefix replay retains its existing evaluation and errors

#### Scenario: A restored or new run

- **WHEN** a simulation restores or resets a snapshot, or a new simulation owns the model
- **THEN** no standing value from the prior run state is trusted without a successful bind under the current run, and cache storage remains bounded by the run's compiled constraints
