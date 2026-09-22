## MODIFIED Requirements

### Requirement: Rebinding an expression path uses current piece values

The framework SHALL evaluate an expression path at each new piece using that piece's current inputs and branch values, preserving the graph's arithmetic order and error behavior. Repeated binding SHALL NOT reuse numeric results from earlier pieces or retain a discarded machine graph through process-wide bookkeeping. Repeated samples within one piece SHALL reuse the path's immutable evaluation structure without hashing expression-node keys for each sample. A running constraint whose read paths are determined SHALL follow its bound expression as one search-local path, preserving each sampled level and its order; a constraint without those paths SHALL retain prefix replay.

#### Scenario: Standing input changes between pieces

- **WHEN** the same expression path is bound to one set of inputs and then to a different set
- **THEN** its value and later path samples reflect the new inputs with the same arithmetic order

#### Scenario: Failed first binding does not poison later binding

- **WHEN** a path binding fails for a missing input and the path is rebound with complete inputs
- **THEN** the first call reports its normal error and the second produces the normal value

#### Scenario: Discarded path releases its graph

- **WHEN** a path has been bound and its owner discards it
- **THEN** path bookkeeping does not retain the expression graph

#### Scenario: Numeric extrema select the same operand

- **WHEN** a bound path evaluates numeric `min` or `max` values, including equal signed zeros or a NaN operand
- **THEN** it selects the same operand and follows the same error behavior as the full graph evaluator in the original argument order

#### Scenario: Malformed path extremum keeps its arity error

- **WHEN** a bound path `min` or `max` call has other than two operands
- **THEN** it reports the same error as the public two-argument numeric function at that call's place in evaluation order

#### Scenario: Repeated samples after a successful bind

- **WHEN** one expression path is sampled repeatedly at different moving inputs within a piece
- **THEN** each sample uses its current inputs and standing values in the original operation order without repeated expression-node key lookup

#### Scenario: Failed later bind leaves the prior piece intact

- **WHEN** an expression path is successfully bound, then a later bind fails before completion
- **THEN** that failure retains its original error and cannot partially publish the later piece's values or evaluation structure

#### Scenario: Determined constraint reads follow one search-local path

- **WHEN** a running bound reads determined paths during a searched stop
- **THEN** every existing sample and bisection compares the same level in the same order, with the bound's own coordinate held at the tick-start value and standing reads refreshed at the next search

#### Scenario: Opposite signed-zero endpoints remain distinct

- **WHEN** a determined read path reports numerically equal signed-zero endpoints with different sign bits
- **THEN** the searched bound evaluates each endpoint's actual bit pattern rather than freezing one endpoint as a standing value

#### Scenario: Undetermined reads still replay their prefix

- **WHEN** a required read has no determined motion path
- **THEN** the constraint still replays its sub-program at each existing search fraction, retaining the same result and refusal behavior
