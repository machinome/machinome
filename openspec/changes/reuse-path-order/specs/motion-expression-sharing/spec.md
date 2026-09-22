## ADDED Requirements

### Requirement: Rebinding an expression path uses current piece values

The framework SHALL evaluate an expression path at each new piece using that piece's current inputs and branch values, preserving the graph's arithmetic order and error behavior. Repeated binding SHALL NOT reuse numeric results from earlier pieces or retain a discarded machine graph through process-wide bookkeeping.

#### Scenario: Standing input changes between pieces

- **WHEN** the same expression path is bound to one set of inputs and then to a different set
- **THEN** its value and later path samples reflect the new inputs with the same arithmetic order

#### Scenario: Failed first binding does not poison later binding

- **WHEN** a path binding fails for a missing input and the path is rebound with complete inputs
- **THEN** the first call reports its normal error and the second produces the normal value

#### Scenario: Discarded path releases its graph

- **WHEN** a path has been bound and its owner discards it
- **THEN** path bookkeeping does not retain the expression graph
