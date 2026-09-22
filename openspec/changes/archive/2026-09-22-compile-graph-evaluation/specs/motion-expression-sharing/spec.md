## MODIFIED Requirements

### Requirement: Repeated numerical evaluation preserves shared expression semantics

The framework SHALL evaluate a shared expression against each supplied input mapping with the same arithmetic order and error behavior, including when the same expression is evaluated repeatedly. Processing repeated evaluations SHALL NOT keep a discarded expression graph alive through a process-wide registry.

#### Scenario: One shared expression at several input values

- **WHEN** one shared expression is evaluated repeatedly with different numeric inputs
- **THEN** each result follows the graph's original operation order and the current inputs, without using an earlier numeric result

#### Scenario: Missing input after a successful evaluation

- **WHEN** a shared expression evaluates successfully and is then evaluated without a required input
- **THEN** the second evaluation reports the same unresolved-input error as a first evaluation would

#### Scenario: Discarded evaluated expression is collectible

- **WHEN** an expression is evaluated, then all its owners release it
- **THEN** evaluation bookkeeping does not keep the expression alive

#### Scenario: Full-graph extrema keep numeric operand identity

- **WHEN** a shared expression containing numeric `min` or `max` is evaluated repeatedly with signed-zero, NaN, or changing operands
- **THEN** every result selects the same operand in the same argument order as its first numerical evaluation

#### Scenario: Malformed full-graph extremum keeps its arity error

- **WHEN** a full-graph `min` or `max` call has other than two operands
- **THEN** it reports the same error as the public two-argument numeric function at that call's place in evaluation order

#### Scenario: An earlier error keeps precedence over a later unsupported operation

- **WHEN** an expression has a failing input or arithmetic node before an unsupported operation in its evaluation order
- **THEN** evaluation reports the earlier failure first, including on repeated calls

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

#### Scenario: Numeric extrema select the same operand

- **WHEN** a bound path evaluates numeric `min` or `max` values, including equal signed zeros or a NaN operand
- **THEN** it selects the same operand and follows the same error behavior as the full graph evaluator in the original argument order

#### Scenario: Malformed path extremum keeps its arity error

- **WHEN** a bound path `min` or `max` call has other than two operands
- **THEN** it reports the same error as the public two-argument numeric function at that call's place in evaluation order
