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

#### Scenario: Repeated binary evaluation retains IEEE operand order

- **WHEN** a shared binary expression is evaluated repeatedly with changing finite, signed-zero or nonfinite numeric inputs
- **THEN** each numeric result or error retains the original Python operation and operand order, without replacing a later evaluation with an earlier result
