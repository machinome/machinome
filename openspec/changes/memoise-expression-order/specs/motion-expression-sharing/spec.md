## ADDED Requirements

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
